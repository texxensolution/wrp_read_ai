import os
import json
import librosa
import time
from typing import Dict, Any
from src.modules.common.utilities import download_mp3
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

    def evaluate(self, payload: Dict[str, Any]):
        audio_url = payload['audio_url']
        user_id = payload["user_id"]
        email = payload["email"]
        given_transcription = payload["given_transcription"]
        script_id = payload['script_id']
        record_id = payload['record_id']

        filename = os.path.join('storage', 'script_reading', f"{user_id}-{email}.mp3")

        # print(filename)
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
                print('record_id', record_id)
                print('response', response)
                raise Exception("File mark as deleted")

            # mp3 to wav conversion
            converted_audio_path = AudioConverter.convert_mp3_to_wav(filename)
            # print('converted', converted_audio_path)

            print('📜 transcribing...')
            speaker_transcription = self.transcriber.transcribe_with_google(audio_path=converted_audio_path)
            
            print('⚖️  evaluating script reading...')
            evaluation_result = self.script_reading_evaluation(
                given_script=given_transcription,
                transcription=speaker_transcription,
                script_id=script_id,
                audio_path=filename
            )

            # add audio path
            evaluation_result["audio_path"] = filename

            return evaluation_result
            
        except Exception as err:
            
            print(f"Error: {err}")
            # raise Exception("Error Script Reading Evaluation: ", err)
    
    def process(self, task: Task):
        try:
            payload = task.payload
            record_id = payload['record_id']
            # evaluation and download the file first
            evaluation = self.evaluate(payload)
            audio_path = evaluation['audio_path']
            file_token = self.file_manager.upload(audio_path)

            # predicted classification
            predicted_classification = "Good" if evaluation['classification'] == 1 else "Bad"
            # print("classification: ", evaluation['classification'], predicted_classification)

            request_payload = LarkPayloadBuilder.builder() \
                .add_key_value('email', payload['email']) \
                .add_key_value('name', payload['name']) \
                .add_key_value('script_id', payload['script_id']) \
                .add_key_value('parent_record_id', record_id) \
                .add_key_value('result', evaluation['result']) \
                .add_key_value('audio_duration_seconds', evaluation['audio_duration']) \
                .add_key_value('avg_pause_duration', evaluation['avg_pause_duration']) \
                .add_key_value('words_per_minute', evaluation['words_per_minute']) \
                .add_key_value('transcription', evaluation['transcription']) \
                .add_key_value('given_transcription', evaluation['given_transcription']) \
                .add_key_value('pronunciation', evaluation['pronunciation_score']) \
                .add_key_value('enunciation', evaluation['score_object']['enunciation']) \
                .add_key_value('clarityofexpression', evaluation['score_object']['clarityofexpression']) \
                .add_key_value('similarity_score', evaluation['similarity_score']) \
                .add_key_value('predicted_classification', predicted_classification) \
                .add_key_value('evaluation', evaluation['evaluation']) \
                .add_key_value('wpm_category', evaluation['wpm_category']) \
                .add_key_value('pitch_consistency', evaluation['pitch_consistency']) \
                .add_key_value('pacing_score', evaluation['pacing_score']) \
                .add_key_value('metadata', evaluation['metadata']) \
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

            return is_done
        except Exception as err:
            print(f"ScriptReadingProcess error: {err}")
            return False


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

    def script_reading_evaluation(self, given_script: str, transcription: str, script_id: str, audio_path: str):
        try:
            y, sr = librosa.load(audio_path)
            avg_pause_duration = FeatureExtractor.load_audio(y, sr).calculate_pause_duration()
            # print("pause_ duration", avg_pause_duration)
            audio_duration = librosa.get_duration(y=y, sr=sr)
            # print("audio_duration", audio_duration)
            processed_transcription = TextPreprocessor.normalize(transcription)
            # print("processed_transcription", processed_transcription)
            given_script = TextPreprocessor.normalize_text_with_new_lines(given_script)
            # print("given_script", given_script)
            words_per_minute = AudioProcessor.calculate_words_per_minute(processed_transcription, audio_duration)
            # print("wpm", words_per_minute)
            similarity_score = TranscriptionProcessor.compute_distance(given_script, transcription)
            # print("similarity", similarity_score)
            # pitch_std = FeatureExtractor.load_audio(y, sr).pitch_consistency()
            pitch_std = FeatureExtractor.load_audio(y, sr).pitch_consistency()
            metadata = FeatureExtractor.load_audio(y, sr).extract_audio_quality_as_json()
            # print("pitch_std", pitch_std)
            pitch_consistency = AudioProcessor.determine_pitch_consistency(pitch_std)
            # print("pitch_cons", pitch_consistency)
            prompt = self.generate_prompt(
                speaker_transcript=transcription, 
                given_transcript=given_script
            )
            # print("prompt", prompt)
            result = self.eloquent.evaluate(prompt)
            # print("result", result)
            captured_json_result = TextPreprocessor.get_json_from_text(result)
            # print("captured_json_result", captured_json_result)
            evaluation = TextPreprocessor.remove_json_object_from_texts(result)
            # print("evaluation", evaluation)
            wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
            # print("wpm_category", wpm_category)
            pacing_score = AudioProcessor.determine_speaker_pacing(words_per_minute, avg_pause_duration)
            # print("pacing_score", pacing_score)
            classification = self.classifier.predict(y, sr)
            # print("classification", classification)
            pronunciation_score = PhonemicAnalysis(
                transcription=transcription,
                script_id=script_id
            ).run_analysis(y, sr)

            # print('pronunciation', pronunciation_score)
            scores = {
                "result": result,
                "avg_pause_duration": avg_pause_duration,
                "audio_duration": audio_duration,
                "words_per_minute": words_per_minute,
                "transcription": processed_transcription,
                "given_transcription": given_script,
                "similarity_score": similarity_score,
                "score_object": captured_json_result,
                "evaluation": evaluation.strip(),
                "audio_path": audio_path,
                "wpm_category": wpm_category,
                "classification": classification,
                "pitch_consistency": pitch_consistency,
                "pacing_score": pacing_score,
                "pronunciation_score": pronunciation_score,
                "metadata": metadata
            }

            return scores
        except Exception as err:
            print("Error script reading evaluation:", err)


