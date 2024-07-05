import os
import logging
import time
from dataclasses import dataclass
import librosa
import requests
from loguru import logger
from speech_recognition.exceptions import TranscriptionFailed

from src.modules.builders import LarkPayloadBuilder
from src.modules.common import (AudioConverter, AudioProcessor,
                                FeatureExtractor, FluencyAnalysis, Logger,
                                PhonemicAnalysis, PronunciationAnalyzer, Task,
                                TextPreprocessor, TranscriptionProcessor)
from src.modules.common.utilities import delete_file, download_mp3
from src.modules.exceptions import (AudioIncompleteError,
                                    EvaluationFailureError, FileUploadError)
from src.modules.lark import BitableManager, FileManager
from src.modules.ollama import EloquentOpenAI
from src.modules.whisper import Transcriber


@dataclass
class ScriptReadingEvaluator:
    """this class holds all information for processing script reading"""
    transcriber: Transcriber
    eloquent: EloquentOpenAI
    base_manager: BitableManager
    file_manager: FileManager
    logs_manager: Logger
    fluency_analysis: FluencyAnalysis
    pronunciation_analyzer: PronunciationAnalyzer
    logs: logging.Logger
    destination_table_id: str = os.getenv('SCRIPT_READING_TABLE_ID'),

    def generate_prompt(self, speaker_transcript: str, given_transcript: str):
        """generate llm prompt for openai"""
        return f"""
            Instruction:
            Language: Tagalog, English
            Evaluate the transcription based on the criteria below and give brief description on how you evaluate the criterias
            Criterias:
                - Compare the two Speaker Transcription and Given Script
                - Include the mispronunciation between speaker transcription and given script

            Speaker Transcription: {speaker_transcript}
            Given Script: {given_transcript}
        """

    async def upload_audio_to_lark(self, filename):
        """helper for uploading file to lark asynchronously"""
        try:
            print("📤 uploading file to lark base...")
            # file_token = self.file_manager.upload(filename)
            file_token = await self.file_manager.upload_async(filename)
            return file_token
        except Exception as err:
            raise Exception(err)
    
    def create_audio_path(self, user_id: str, email: str) -> str:
        """helper for generating path for audio path living in storage/scriptreading folder"""
        return os.path.join('storage', 'script_reading', f"{user_id}-{email}.mp3")

    async def process(self, task: Task):
        """process function will perform all validation and evaluation for script reading"""
        time_start = time.time()
        try:
            payload = task.payload
            user_id = payload["user_id"]
            email = payload["email"]
            record_id = payload['record_id']
            audio_url = payload['audio_url']
            script_id = payload['script_id']
            name = payload['name']

            no_of_retries = int(payload['no_of_retries'])
            given_transcription = payload['given_transcription']

            filename = self.create_audio_path(user_id, email)

            # download the mp3 file
            download_mp3(audio_url, filename)

            # mp3 to wav conversion
            converted_audio_path = AudioConverter.convert_mp3_to_wav(filename)

            file_token = await self.upload_audio_to_lark(filename)

            self.logs.info('📜 transcribing...')
            # transcription = self.transcriber.transcribe_with_google(converted_audio_path)
            transcription = await self.transcriber.transcribe_with_deepgram_async(converted_audio_path)
            transcription = TextPreprocessor.normalize(transcription)
            given_transcription = TextPreprocessor.normalize_text_with_new_lines(given_transcription)
           
            self.logs.info('⚖️  evaluating script reading...')
            y, sr = librosa.load(converted_audio_path)
            audio_duration = librosa.get_duration(y=y)
            audio_is_more_than_30_secs = AudioProcessor.is_audio_more_than_30_secs(y, sr)

            if not audio_is_more_than_30_secs:
                raise AudioIncompleteError(
                    name=name,
                    audio_path=converted_audio_path,
                    message="Audio file is less than 30 secs."
                )

            self.logs.info("🎯 calculating similarity score...")
            similarity_score = self.similarity_score(transcription, given_transcription)
            self.logs.info("🎶 extracting audio features...")
            avg_pause_duration = FeatureExtractor(y, sr).calculate_pause_duration()
            pitch_consistency = AudioProcessor.pitch_stability_score(y, sr)
            words_per_minute = AudioProcessor.calculate_words_per_minute(transcription, audio_duration)
            wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
            pronunciation_score = self.pronunciation_analyzer.predict(converted_audio_path)
            evaluation, cost = await self.async_ai_grading(transcription, given_transcription)
            pacing_score = AudioProcessor.determine_speaker_pacing(words_per_minute, avg_pause_duration)
            self.logs.info("🧐 calculating fluency of the speaker..." )
            fluency = self.fluency_analysis.analyze(converted_audio_path)
        
            time_end = time.time()
            processing_duration = time_end - time_start

            self.logs.info("📦 packaging payload...")
            request_payload = LarkPayloadBuilder.builder() \
                .add_key_value('email', email) \
                .add_key_value('name', name) \
                .add_key_value('script_id', script_id) \
                .add_key_value('parent_record_id', record_id) \
                .add_key_value('audio_duration_seconds', audio_duration) \
                .add_key_value('avg_pause_duration', avg_pause_duration) \
                .add_key_value('words_per_minute', words_per_minute) \
                .add_key_value('transcription', transcription) \
                .add_key_value('given_transcription', given_transcription) \
                .add_key_value('pronunciation', pronunciation_score) \
                .add_key_value('similarity_score', similarity_score) \
                .add_key_value('evaluation', evaluation) \
                .add_key_value('wpm_category', wpm_category) \
                .add_key_value('pitch_consistency', pitch_consistency) \
                .add_key_value('pacing_score', pacing_score) \
                .add_key_value('fluency', fluency) \
                .add_key_value('processing_duration', processing_duration) \
                .attach_media_file_token('audio', file_token) \
                .add_key_value('request_cost', cost) \
                .build()

            print("📤 uploading a record on lark base...")
            await self.base_manager.create_record_async(
                table_id=os.getenv('SCRIPT_READING_TABLE_ID'), 
                fields=request_payload
            )
            
            self.logs.info("✔️ marking record as done...")
            # update the record and mark as done
            await self.mark_current_record_as_done(
                table_id=os.getenv("BUBBLE_TABLE_ID"),
                record_id=record_id
            )
            
            remarks = self.calculate_remarks(
                pronunciation=pronunciation_score,
                wpm_category=wpm_category,
                similarity_score=similarity_score,
                pitch_consistency=pitch_consistency,
                pacing_score=pacing_score,
                fluency=fluency
            )
            delete_file(filename)
            delete_file(converted_audio_path)

            if remarks >= 80:
                self.logs.info("✔️  done processing: name=%s, remarks: ✅, score: %s, processing duration: %s\n\n", name, remarks, processing_duration)
            else:
                self.logs.info("✔️  done processing: name=%s, remarks: ❌, score: %s, processing_duration: %s\n\n", name, remarks, processing_duration)

        except requests.exceptions.InvalidURL as err:
            await self.base_manager.update_record_async(
                table_id=os.getenv('BUBBLE_TABLE_ID'), 
                record_id=record_id, 
                fields={
                    "status": "invalid audio url"
                }
            )
            await self.logs_manager.create_record_async(
                message=err,
                error_type="Invalid Http Url"
            )
            logger.error(f"applicant name: {name}, message: {err}")
            self.logs.error("applicant name: %s, message: %s", name, err)
        
        except FileUploadError as err:
            await self.logs_manager.create_record_async(
                message=err,
                error_type="File Token Missing"
            )
            logger.error(err)
            self.logs.error(err)

        except AudioIncompleteError as err:
            await self.base_manager.update_record_async(
                table_id=os.getenv("BUBBLE_TABLE_ID"),
                record_id=record_id,
                fields={
                    "status": "audio_less_than_30_secs"
                }
            )
            # logger.error(f"applicant name: {name}, message: audio is less than 30 secs")
            self.logs.error("applicant name: %s, message: audio is less than 30 secs", name)

        except TranscriptionFailed as err:
            await self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )

            await self.logs_manager.create_record_async(
                message=err,
                error_type='Transcribing Failure'
            )

            logger.error(f"transcription failure: {err}")
            self.logs.error("transcription failure: %s", err)

        except EvaluationFailureError as err:
            await self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )
            await self.logs_manager.create_record_async(
                message=err,
                error_type='Evaluation Failure'
            )
            self.logs.error("evaluation failure: %s", err)

        except requests.exceptions.RequestException as err:
            await self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )
            await self.logs_manager.create_record_async(
                message=err,
                error_type='Audio Downloading'
            )
            self.logs.error("request exception: %s", err)

        except Exception as err:
            print(f"❗ General error: {err}")
            await self.logs_manager.create_record_async(
                message=err,
                error_type='General Error'
            )
            await self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )
            time.sleep(3)
            return False
            
    def calculate_remarks(self, pronunciation: float, wpm_category: int, similarity_score: float, pitch_consistency: int, pacing_score: int, fluency: int):
        """calculating remarks"""
        score = (((pronunciation / 5) * 0.25) + ((fluency / 5) * 0.15) + ((wpm_category / 5) * 0.15) + ((similarity_score / 5) * 0.25) + ((pitch_consistency / 5) * 0.10) + ((pacing_score / 5) * 0.10)) * 100
        return round(score)

    async def update_number_of_retries(self, record_id: str, previous_count: int):
        """update number of retry when the worker is failed processing"""
        try:
            await self.base_manager.update_record_async(
                table_id=os.getenv('BUBBLE_TABLE_ID'),
                record_id=record_id,
                fields={
                    "no_of_retries": previous_count + 1
                }
            )
        except Exception as err:
            print(f"❗ Updating retry count failed: {err}")

    async def mark_current_record_as_done(self, table_id: str, record_id: str):
        """mark current record as done when the worker is done at processing it"""
        try:
            await self.base_manager.update_record_async(
                table_id=table_id, 
                record_id=record_id, 
                fields={
                    "status": "done"
                }
            )
        except Exception as err:
            raise Exception(f"Error: message=%s, status= updating record failed: %s", err, record_id)
        
    async def current_record_dont_have_recording(self, table_id: str, record_id: str):
        """mark record as dont have recording"""
        try:
            await self.base_manager.update_record_async(
                table_id=table_id,
                record_id=record_id,
                fields={
                    "status": "file deleted"
                }
            )
            return True
        except Exception as err:
            raise Exception(f"Error: %s, error_type=❗ Updating record failed: %s", err, record_id)
    
    def pronunciation_grading(self, transcription: str, script_id: str, y, sr):
        return PhonemicAnalysis(
            transcription=transcription,
            script_id=script_id
        ).run_analysis(y, sr)
    
    
    def similarity_score(self, transcription: str, given_script: str):
        return TranscriptionProcessor.compute_distance(
            transcription=transcription,
            given_script=given_script
        )
    
    def pitch_stability_score(self, y, sr):
        pitch_std = FeatureExtractor(y, sr).pitch_consistency()
        return AudioProcessor.determine_pitch_consistency(pitch_std)

    def calculate_wpm(self, transcription: str, audio_duration):
        return AudioProcessor.calculate_words_per_minute(transcription, audio_duration)
    
    def ai_grading(self, transcription: str, given_script: str):
        combined_prompt = self.generate_prompt(
            speaker_transcript=transcription,
            given_transcript=given_script
        )

        result, cost = self.eloquent.evaluate(combined_prompt)

        return result, cost

    async def async_ai_grading(self, transcription: str, given_script: str):
        combined_prompt = self.generate_prompt(
            speaker_transcript=transcription,
            given_transcript=given_script
        )

        result, cost = await self.eloquent.evaluate_async(combined_prompt)

        return result, cost