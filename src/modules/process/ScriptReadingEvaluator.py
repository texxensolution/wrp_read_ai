import os
import librosa
import time
import requests
from speech_recognition.exceptions import TranscriptionFailed
from loguru import logger
from src.modules.exceptions import AudioIncompleteError, EvaluationFailureError, FileUploadError
from src.modules.common.utilities import download_mp3, retry, delete_file
from src.modules.ollama import EloquentOpenAI
from src.modules.whisper import Transcriber
from src.modules.lark import BitableManager, FileManager
from src.modules.builders import LarkPayloadBuilder
from src.modules.common import Task, AudioConverter, AudioProcessor, TextPreprocessor, TranscriptionProcessor, FeatureExtractor, VoiceClassifier, FluencyAnalysis, PronunciationAnalyzer
from src.modules.common import PhonemicAnalysis
from src.modules.common import Logger
from dataclasses import dataclass

@dataclass
class ScriptReadingEvaluator:
    transcriber: Transcriber
    eloquent: EloquentOpenAI
    base_manager: BitableManager
    file_manager: FileManager
    classifier: VoiceClassifier
    logs_manager: Logger
    fluency_analysis: FluencyAnalysis
    pronunciation_analyzer: PronunciationAnalyzer
    destination_table_id: str = os.getenv('SCRIPT_READING_TABLE_ID'),

    def generate_prompt(self, speaker_transcript: str, given_transcript: str):
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

    def upload_audio_to_lark(self, filename):
        try:
            print("📤 uploading file to lark base...")
            file_token = self.file_manager.upload(filename)
            return file_token
        except Exception as err:
            raise Exception(err)
    
    def create_audio_path(self, user_id: str, email: str) -> str:
        return os.path.join('storage', 'script_reading', f"{user_id}-{email}.mp3")

    def process(self, task: Task):
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

            file_token = self.upload_audio_to_lark(filename)

            print('📜 transcribing...')
            # transcription = self.transcriber.transcribe_with_google(converted_audio_path)
            transcription = self.transcriber.transcribe_with_deepgram(converted_audio_path)
            transcription = TextPreprocessor.normalize(transcription)
            given_transcription = TextPreprocessor.normalize_text_with_new_lines(given_transcription)
           
            print('⚖️  evaluating script reading...')
            y, sr = librosa.load(converted_audio_path)
            audio_duration = librosa.get_duration(y=y)
            audio_is_more_than_30_secs = AudioProcessor.is_audio_more_than_30_secs(y, sr)

            if not audio_is_more_than_30_secs:
                raise AudioIncompleteError(
                    name=name,
                    audio_path=converted_audio_path,
                    message="Audio file is less than 30 secs."
                )

            print("🎯 calculating similarity score...")
            similarity_score = self.similarity_score(transcription, given_transcription)
            print("🎶 extracting audio features...")
            avg_pause_duration = FeatureExtractor(y, sr).calculate_pause_duration()
            pitch_consistency = AudioProcessor.pitch_stability_score(y, sr)
            words_per_minute = AudioProcessor.calculate_words_per_minute(transcription, audio_duration)
            wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
            pronunciation_score = self.pronunciation_analyzer.predict(converted_audio_path)
            # pronunciation_score = self.pronunciation_grading(
            #     transcription=transcription,
            #     script_id=script_id,
            #     y=y,
            #     sr=sr
            # )
            evaluation, cost = self.ai_grading(transcription, given_transcription)
            pacing_score = AudioProcessor.determine_speaker_pacing(words_per_minute, avg_pause_duration)
            # metadata = FeatureExtractor(y, sr).extract_audio_quality_as_json()
            print("🔊 calculating voice classification...")
            # voice_classification = self.voice_classification(y, sr)
            # predicted_classification = "Good" if voice_classification == 1 else "Bad"
            print("🧐 calculating fluency of the speaker..." )
            fluency = self.fluency_analysis.analyze(converted_audio_path)
        
            time_end = time.time()
            processing_duration = time_end - time_start

            print("📦 packaging payload...")
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
                # .add_key_value('metadata', metadata) \
                # .add_key_value('predicted_classification', predicted_classification) \

            print("📤 uploading a record on lark base...")
            response = self.base_manager.create_record(
                table_id=os.getenv('SCRIPT_READING_TABLE_ID'), 
                fields=request_payload
            )
            
            print("✔️ marking record as done...")
            # update the record and mark as done
            self.mark_current_record_as_done(
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
                print(f"✔️  done processing: name={name}, remarks: ✅, score: {remarks}, processing duration: {processing_duration}\n\n")
            else:
                print(f"✔️  done processing: name={name}, remarks: ❌, score: {remarks}, processing_duration: {processing_duration}\n\n")

        except requests.exceptions.InvalidURL as err:
            response = self.base_manager.update_record(
                table_id=os.getenv('BUBBLE_TABLE_ID'), 
                record_id=record_id, 
                fields={
                    "status": "invalid audio url"
                }
            )
            logger.error(f"applicant name: {name}, message: invalid audio url")
        
        except FileUploadError as err:
            self.logs_manager.create_record(
                message=err,
                error_type="File Token Missing"
            )
            logger.error(err)

        except AudioIncompleteError as err:
            self.base_manager.update_record(
                table_id=os.getenv("BUBBLE_TABLE_ID"),
                record_id=record_id,
                fields={
                    "status": "audio_less_than_30_secs"
                }
            )
            logger.error(f"applicant name: {name}, message: audio is less than 30 secs")

        except TranscriptionFailed as err:
            
            self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )

            self.logs_manager.create_record(
                message=err,
                error_type='Transcribing Failure'
            )

            logger.error(f"transcription failure: {err}")

        except EvaluationFailureError as err:
            self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )
            
            self.logs_manager.create_record(
                message=err,
                error_type='Evaluation Failure'
            )
            
            logger.error(f"evaluation failure: {err}")

        except requests.exceptions.RequestException as err:
            self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )
            
            self.logs_manager.create_record(
                message=err,
                error_type='Audio Downloading'
            )
            logger.error(f"request exception: {err}")

        except Exception as err:
            print(f"❗ General error: {err}")
            self.logs_manager.create_record(
                message=err,
                error_type='General Error'
            )
            self.update_number_of_retries(
                record_id=record_id,
                previous_count=no_of_retries
            )
            time.sleep(3)
            return False
            
    def calculate_remarks(self, pronunciation: float, wpm_category: int, similarity_score: float, pitch_consistency: int, pacing_score: int, fluency: int):
        score = (((pronunciation / 5) * 0.25) + ((fluency / 5) * 0.15) + ((wpm_category / 5) * 0.15) + ((similarity_score / 5) * 0.25) + ((pitch_consistency / 5) * 0.10) + ((pacing_score / 5) * 0.10)) * 100
        return round(score)

    def update_number_of_retries(self, record_id: str, previous_count: int):
        try:
            self.base_manager.update_record(
                table_id=os.getenv('BUBBLE_TABLE_ID'),
                record_id=record_id,
                fields={
                    "no_of_retries": previous_count + 1
                }
            )
        except Exception as err:
            print(f"❗ Updating retry count failed:", err)

    def mark_current_record_as_done(self, table_id: str, record_id: str):
        try:
            response = self.base_manager.update_record(
                table_id=table_id, 
                record_id=record_id, 
                fields={
                    "status": "done"
                }
            )
        except Exception as err:
            raise Exception(f"Updating record failed: {record_id}")
        
    def current_record_dont_have_recording(self, table_id: str, record_id: str):
        try:
            response = self.base_manager.update_record(
                table_id=table_id, 
                record_id=record_id, 
                fields={
                    "status": "file deleted"
                }
            )
            return True
        except Exception as err:
            raise Exception(f"❗ Updating record failed: {record_id}")
    
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

    def voice_classification(self, y, sr):
        return self.classifier.predict(y, sr)
    
    def extract_metadata(self, y, sr):
        return FeatureExtractor(y, sr).extract_audio_quality_as_json()

    def calculate_wpm(self, transcription: str, audio_duration):
        return AudioProcessor.calculate_words_per_minute(transcription, audio_duration)

    def ai_grading(self, transcription: str, given_script: str):
        combined_prompt = self.generate_prompt(
            speaker_transcript=transcription,
            given_transcript=given_script
        )

        result, cost = self.eloquent.evaluate(combined_prompt)

        return result, cost


