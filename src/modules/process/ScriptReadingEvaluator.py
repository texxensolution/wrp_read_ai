import os
import json
import librosa
import time
from typing import Dict, Any
from src.modules.common.utilities import download_mp3, retry
from src.modules.ollama import EloquentOpenAI
from src.modules.whisper import Transcriber
from src.modules.lark import BitableManager, FileManager
from src.modules.builders import LarkPayloadBuilder
from src.modules.common import Task, AudioConverter, AudioProcessor, TextPreprocessor, TranscriptionProcessor, FeatureExtractor, VoiceClassifier
from src.modules.common import PhonemicAnalysis
from dataclasses import dataclass

@dataclass
class ScriptReadingEvaluator:
    transcriber: Transcriber
    eloquent: EloquentOpenAI
    base_manager: BitableManager
    file_manager: FileManager
    classifier: VoiceClassifier
    destination_table_id: str = os.getenv('SCRIPT_READING_TABLE_ID')

    def generate_prompt(self, speaker_transcript: str, given_transcript: str):
        return f"""
            Instruction:
            Language: Tagalog, English
            Evaluate the transcription based on the criteria below and include the scores in json format output and brief description on how you evaluate the criterias
            Json Object: pronunciation, enunciation, clarityofexpression, grammarandsyntax

            Criterias:
                    - Pronunciation: Assess the accuracy of word pronunciations according to standard language conventions. Provide a score from 1 (poor) to 5 (excellent).
                    - Enunciation: Evaluate the clarity and precision in articulating individual sounds and words. Assign a score from 1 (unclear) to 5 (crystal clear).
                    - Clarity of Expression: Assess how clearly the participant communicates ideas and concepts, avoiding ambiguity or confusion. Provide a score from 1 (unclear) to 5 (crystal clear).
                    - Grammar and Syntax: Evaluate the correctness of the participant's grammar and sentence structure. Provide a score from 1 (poor) to 5 (excellent).
                    - Compare the two Speaker Transcription and Given Script

            Penalty System:
            Speaker Transcription: {speaker_transcript}
            Given Script: {given_transcript}
        """

    @retry()
    def upload_audio_to_lark(self, filename):
        try:
            print("📤 uploading file to lark base...")
            file_token = self.file_manager.upload(filename)
            return file_token
        except Exception as err:
            print("❗❗❗ Uploading failed:", err)
            return None

    
    def process(self, task: Task):
        try:
            payload = task.payload
            user_id = payload["user_id"]
            email = payload["email"]
            record_id = payload['record_id']
            audio_url = payload['audio_url']
            script_id = payload['script_id']
            name = payload['name']
            given_transcription = payload['given_transcription']

            filename = os.path.join('storage', 'script_reading', f"{user_id}-{email}.mp3")

            try:
                # download the mp3 file
                is_downloaded = download_mp3(audio_url, filename)

                if not is_downloaded:
                    response = self.base_manager.update_record(
                        table_id=os.getenv('BUBBLE_TABLE_ID'), 
                        record_id=record_id, 
                        fields={
                            "status": "file deleted"
                        }
                    )
                    raise Exception("File mark as deleted")
            except Exception as err:
                print("❗❗❗ Audio downloading failed: ", err)

            # mp3 to wav conversion
            converted_audio_path = AudioConverter.convert_mp3_to_wav(filename)

            file_token = self.upload_audio_to_lark(filename)

            if not file_token:
                print("❗❗❗ Mark as failed task")
                return

            try:
                print('📜 transcribing...')
                transcription = self.transcriber.transcribe_with_google(converted_audio_path)
                transcription = TextPreprocessor.normalize(transcription)
                given_transcription = TextPreprocessor.normalize_text_with_new_lines(given_transcription)
            except Exception as err:
                print("❗❗❗ Transcribing failed: ", err)

            try:
                print('⚖️  evaluating script reading...')
                y, sr = librosa.load(converted_audio_path)
                audio_duration = librosa.get_duration(y=y)
                similarity_score = self.similarity_score(transcription, given_transcription)
                avg_pause_duration = FeatureExtractor(y, sr).calculate_pause_duration()
                pitch_std = FeatureExtractor(y, sr).pitch_consistency()
                pitch_consistency = AudioProcessor.determine_pitch_consistency(pitch_std)
                words_per_minute = AudioProcessor.calculate_words_per_minute(transcription, audio_duration)
                wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
                pronunciation_score = self.pronunciation_grading(
                    transcription=transcription,
                    script_id=script_id,
                    y=y,
                    sr=sr
                )
                result, evaluation, score_json = self.ai_grading(transcription, given_transcription)
                pacing_score = AudioProcessor.determine_speaker_pacing(words_per_minute, avg_pause_duration)
                metadata = FeatureExtractor(y, sr).extract_audio_quality_as_json()
                voice_classification = self.voice_classification(y, sr)
                predicted_classification = "Good" if voice_classification == 1 else "Bad"
            except Exception as err:
                print("❗❗❗ Evaluation failed: ", err)

            # evaluation and download the file first
            # evaluation = self.evaluate(payload)
            # audio_path = evaluation['audio_path']
            # file_token = self.file_manager.upload(audio_path)

            # predicted classification

            request_payload = LarkPayloadBuilder.builder() \
                .add_key_value('email', email) \
                .add_key_value('name', name) \
                .add_key_value('script_id', script_id) \
                .add_key_value('parent_record_id', record_id) \
                .add_key_value('result', result) \
                .add_key_value('audio_duration_seconds', audio_duration) \
                .add_key_value('avg_pause_duration', avg_pause_duration) \
                .add_key_value('words_per_minute', words_per_minute) \
                .add_key_value('transcription', transcription) \
                .add_key_value('given_transcription', given_transcription) \
                .add_key_value('pronunciation', pronunciation_score) \
                .add_key_value('enunciation', score_json['enunciation']) \
                .add_key_value('clarityofexpression', score_json['clarityofexpression']) \
                .add_key_value('similarity_score', similarity_score) \
                .add_key_value('predicted_classification', predicted_classification) \
                .add_key_value('evaluation', evaluation) \
                .add_key_value('wpm_category', wpm_category) \
                .add_key_value('pitch_consistency', pitch_consistency) \
                .add_key_value('pacing_score', pacing_score) \
                .add_key_value('metadata', metadata) \
                .attach_media_file_token('audio', file_token) \
                .build()

            response = self.base_manager.create_record(
                table_id=os.getenv('SCRIPT_READING_TABLE_ID'), 
                fields=request_payload
            )

            # update the record and mark as done
            is_done = self.mark_current_record_as_done(
                table_id=os.getenv("BUBBLE_TABLE_ID"),
                record_id=record_id
            )

            if is_done:
                remarks = self.calculate_remarks(
                    pronunciation=pronunciation_score,
                    enunciation=int(score_json['enunciation']),
                    wpm_category=wpm_category,
                    similarity_score=similarity_score,
                    pitch_consistency=pitch_consistency,
                    pacing_score=pacing_score,
                    clarity=score_json['clarityofexpression']
                )

                if remarks >= 80:
                    print(f"done processing: name={name}, remarks: ✅, score: {remarks}\n\n")
                else:
                    print(f"done processing: name={name}, remarks: ❌, score: {remarks}\n\n")

            return is_done
        except Exception as err:
            print(f"❗❗❗ ScriptReadingProcess error: {err}")
            return False


    def calculate_remarks(self, pronunciation, enunciation, wpm_category, similarity_score, pitch_consistency, pacing_score, clarity):
        score = (((pronunciation / 5) * 0.20) + ((enunciation / 5) * 0.20) + ((wpm_category / 5) * 0.15) + ((similarity_score / 5) * 0.20) + ((pitch_consistency / 5) * 0.10) + ((pacing_score / 5) * 0.10) + ((clarity / 5) * 0.05)) * 100
        return round(score)


    def mark_current_record_as_done(self, table_id: str, record_id: str):
        try:
            response = self.base_manager.update_record(
                table_id=table_id, 
                record_id=record_id, 
                fields={
                    "status": "done"
                }
            )
            return True
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
            raise Exception(f"Updating record failed: {record_id}")
    
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

        result = self.eloquent.evaluate(combined_prompt)

        evaluation = TextPreprocessor.remove_json_object_from_texts(result)
        evaluation_json = TextPreprocessor.get_json_from_text(result)

        return result, evaluation, evaluation_json


