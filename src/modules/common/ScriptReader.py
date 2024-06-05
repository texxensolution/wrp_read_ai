import os
from typing import Dict, Any
from src.modules.common.utilities import download_mp3
from src.modules.ollama import EloquentOpenAI
from src.modules.whisper import Transcriber
from src.modules.lark import BitableManager, FileManager
from src.modules.builders import ScriptReadingPayloadBuilder
from src.modules.common import Task
from dataclasses import dataclass

@dataclass
class ScriptReader:
    transcriber: Transcriber
    eloquent: EloquentOpenAI
    base_manager: BitableManager
    file_manager: FileManager
    destination_table_id: str
    script_reading_payload_builder: ScriptReadingPayloadBuilder = ScriptReadingPayloadBuilder()


    def evaluate(self, payload: Dict[str, Any]):
        audio_url = payload['audio_url']
        user_id = payload["user_id"]
        email = payload["email"]
        given_transcription = payload["given_transcription"]

        filename = os.path.join('storage', 'script_reading', f"{user_id}-{email}.mp3")

        try:
            # download the mp3 file
            is_downloaded = download_mp3(audio_url, filename)

            print('📜 transcribing...')
            speaker_transcription = self.transcriber.transcribe_with_google(filename)
            
            print('⚖️  evaluating script reading...')
            evaluation_result = self.eloquent.script_reading_evaluation(
                given_script=given_transcription,
                transcription=speaker_transcription,
                audio_path=filename
            )

            # add audio path
            evaluation_result["audio_path"] = filename

            print(evaluation_result)

            return evaluation_result
        except Exception as err:
            with open('logs.txt', 'w') as f:
                f.write(err)
            raise Exception("Error Script Reading Evaluation: ", err)
    

    def process(self, task: Task):
        try:
            payload = task.payload
            record_id = payload['record_id']
            evaluation = self.evaluate(payload)
            audio_path = evaluation['audio_path']
            file_token = self.file_manager.upload(audio_path)

            payload = self.script_reading_payload_builder \
                .make(
                    record=payload, 
                    evaluation=evaluation
                ) \
                .attach_file_token(
                    key='audio', 
                    file_token=file_token
                ) \
                .build()

            response = self.base_manager.create_record(
                table_id=self.destination_table_id, 
                fields=payload
            )

            # update the record and mark as done
            is_done = self.mark_current_record_as_done(
                table_id=os.getenv("BUBBLE_TABLE_ID"),
                record_id=record_id
            )

            return is_done
        except Exception as err:
            print("Error:", err)
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

