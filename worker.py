from src.modules.lark import Lark, BitableManager, FileManager
import os
import time
import requests
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime
import pytz
import json
from src.modules.whisper import Transcriber
from src.modules.ollama import EloquentOpenAI
from dataclasses import dataclass
from typing import List, Dict, Any, Callable
import librosa
from queue import Queue
import multiprocessing
from src.modules.builders import QuoteTranslationPayloadBuilder
from src.modules.common import TaskQueue, Task, retry, LarkQueue, DataTransformer, VoiceClassifier
from src.modules.process import ScriptReadingEvaluator

@dataclass
class Worker:
    load_dotenv()
    task_queue: TaskQueue
    lark_queue: LarkQueue 
    script_reader: ScriptReadingEvaluator

    def get_correct_table_id(self, assessment_type: str):
        if assessment_type == "Script Reading":
            return os.getenv('SCRIPT_READING_TABLE_ID')
        elif assessment_type == "Quote Translation":
            return os.getenv('QUOTE_TRANSLATION_TABLE_ID')

    def job_processing_quote_translation(self, record, destination_table_id: str):
        record_id = record["record_id"]

        evaluation = self.process_quote_translation_record(
            record=record,
        )
        
        if evaluation is None:
            return

        audio_path = evaluation['audio_path']

        file_token = self.file_manager.upload(audio_path)

        payload = self.create_quote_translation_payload(
            record=record, 
            evaluation=evaluation
        ) \
            .attach_file_token_to_payload(file_token=file_token) \
            .build_payload()

        print('payload', payload)

        response = self.bitable_manager.create_record(
            table_id=destination_table_id, 
            fields=payload
        )

        # update the record and mark as done
        is_done = self.mark_current_record_as_done(
            table_id=self.bubble_table_id,
            record_id=record_id
        )

        return is_done
    
    def switch_cases(self, task: Task):
        if task.type == 'Script Reading':
            self.script_reader.process(task)
        elif task.type == 'Quote Translation':
            pass
    
    def sync(self):
        print('🚀 syncing from lark...')

        records = self.lark_queue.get_items()

        if len(records) == 0:
            return

        transformed_records = DataTransformer.convert_raw_lark_record_to_dict(
            records, 
            [
                "name",
                "user_id",
                "email",
                "assessment_type",
                "audio_url",
                "given_transcription",
                "status"
            ]
        )

        self.task_queue.enqueue_many(transformed_records)

    def processing(self):
        print("Worker is processing...")

        transformed_records = self.sync()

        while True:
            if not self.task_queue.is_empty():
                task = self.task_queue.pop()

                self.switch_cases(task)
            else:
                self.sync()
                time.sleep(3)

    def mark_current_record_as_done(self, table_id: str, record_id: str):
        try:
            response = self.bitable_manager.update_record(
                table_id=table_id, 
                record_id=record_id, 
                fields={
                    "status": "done"
                }
            )
            return True
        except Exception as err:
            return False

    def get_current_timestamp(self):
        # Get the current datetime
        current_datetime = datetime.now()

        # Format the current datetime as a string
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H-%M-%S")

        return formatted_datetime

if __name__ == '__main__':
    load_dotenv('.env')

    task_queue = TaskQueue()

    lark = Lark(
        app_id=os.getenv("APP_ID"),
        app_secret=os.getenv("APP_SECRET")
    )

    base_manager = BitableManager(
        lark_client=lark,
        bitable_token=os.getenv("BITABLE_TOKEN")
    )

    lark_queue = LarkQueue(
        base_manager=base_manager,
        bitable_table_id=os.getenv("BUBBLE_TABLE_ID")
    )

    file_manager = FileManager(
        lark_client=lark, 
        bitable_token=os.getenv('BITABLE_TOKEN')
    )

    eloquent = EloquentOpenAI()

    transcriber = Transcriber()

    classifier = VoiceClassifier('classifier.joblib')

    script_reader = ScriptReadingEvaluator(
        base_manager=base_manager,
        file_manager=file_manager,
        transcriber=transcriber,
        eloquent=eloquent,
        classifier=classifier
    )

    worker = Worker(
        task_queue=task_queue, 
        lark_queue=lark_queue,
        script_reader=script_reader
    )

    # worker.work()
    worker.processing()