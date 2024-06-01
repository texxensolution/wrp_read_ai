from src.modules.lark import Lark, BitableManager, FileManager
import os
import time
import requests
from dotenv import load_dotenv
from uuid import uuid4
import datetime
import pytz
import json
from src.modules.whisper import Transcriber
from src.modules.ollama import EloquentOpenAI
from dataclasses import dataclass
from typing import List, Dict, Any
import librosa
from queue import Queue
import multiprocessing
from src.modules.enums import AssessmentType
from src.modules.builders import ScriptReadingPayloadBuilder, QuoteTranslationPayloadBuilder

@dataclass
class Worker:
    load_dotenv()
    lark: Lark = Lark(
        app_id=os.getenv('APP_ID'),
        app_secret=os.getenv('APP_SECRET')
    )
    bitable_id: str = os.getenv('BITABLE_ID')
    bitable_token: str = os.getenv('BITABLE_TOKEN')
    bitable_manager: BitableManager = BitableManager(
        lark_client=lark,
        bitable_id=bitable_id,
        bitable_token=bitable_token,
    )
    file_manager: FileManager = FileManager(
        lark_client=lark,
        bitable_token=bitable_token,
    )
    transcriber: Transcriber = Transcriber()
    eloquent: EloquentOpenAI = EloquentOpenAI()
    bubble_table_id = os.getenv('BUBBLE_TABLE_ID')
    processed_table_id = os.getenv('PROCESSED_TABLE_ID')
    is_processing: bool = False
    pending_records = []
    no_of_pending_records = 0
    skipped_records = [] # list of record_id to skipped
    builded_payload = None
    queue: Queue = Queue()
    script_reading_payload_builder = ScriptReadingPayloadBuilder()
    quote_translation_payload_builder = QuoteTranslationPayloadBuilder()

    def __init__(self):
        self.script_reading_table_id = self.get_correct_table_id(AssessmentType.SCRIPT_READING)
        self.quote_translation_table_id = self.get_correct_table_id(AssessmentType.QUOTE_TRANSLATION)

    def remove_skipped_records(self):
        for index, current_record in enumerate(self.pending_records):
            if current_record['record_id'] in self.skipped_records: 
                self.pending_records.pop(index)
            
    def enqueue_pending_records(self, records):
        for record in records:
            status = record.fields.get("status")
            audio_url: str = record.fields.get("audio_url")
            email = record.fields.get("email")
            user_id = record.fields.get("user_id")
            created_date = record.fields.get("created_date")
            given_transcription = record.fields.get("given_transcription")
            assessment_type = record.fields.get("assessment_type")
            name = record.fields.get("name")
            record_id = record.record_id

            current_record = {
                "status": status,
                "audio_url": audio_url,
                "email": email,
                "user_id": user_id,
                "created_date": created_date,
                "given_transcription": given_transcription,
                "assessment_type": assessment_type,
                "record_id": record_id,
                "name": name
            }

            self.queue.put(current_record)
        
    def get_correct_table_id(self, assessment_type: str):
        if assessment_type == "Script Reading":
            return os.getenv('SCRIPT_READING_TABLE_ID')
        elif assessment_type == "Quote Translation":
            return os.getenv('QUOTE_TRANSLATION_TABLE_ID')

    def job_processing_script_reading(self, record, destination_table_id: str):
        record_id = record["record_id"]

        evaluation = self.process_script_reading_record(
            record=record,
        )
        
        if evaluation is None:
            return

        audio_path = evaluation['audio_path']

        file_token = self.file_manager.upload(audio_path)

        # payload = self.create_payload(record=record, evaluation=evaluation) \
        #     .attach_file_token_to_payload(file_token=file_token) \
        #     .build_payload()

        payload = self.script_reading_payload_builder \
            .make(
                record=record, 
                evaluation=evaluation
            ) \
            .attach_file_token(
                key='audio', 
                file_token=file_token
            ) \
            .build()

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

    def work(self):
        print("worker initiated...")
        while True:
            print('📦 current items in the queue: ', self.queue.qsize())
            if not self.queue.empty():
                # fetch lark base items
                record = self.queue.get()
       
                if record['record_id'] in self.skipped_records:
                    continue

                # print(f"number of items to processed: {self.no_of_pending_records}")
                
                # for index, pending_record in enumerate(self.pending_records):
                record_id = record['record_id']
                assessment_type = record['assessment_type']

                destination_table_id = self.get_correct_table_id(assessment_type)

                if assessment_type == "Script Reading":

                    print('⚙️  script reading processing: ', record['record_id'])
                # process the record 
                    is_done = self.job_processing_script_reading(
                        record, 
                        destination_table_id=destination_table_id
                    )

                    if is_done:
                        print('✅ done processing: ', record_id)
                    else:
                        print('❌ failed marking as done: ', record_id)

                elif assessment_type == "Quote Translation":
                    print('⚙️  quote translation processing: ', record['record_id'])
                    is_done = self.job_processing_quote_translation(
                        record, 
                        destination_table_id=destination_table_id
                    )

                    if is_done:
                        print('✅ done processing: ', record_id)
                    else:
                        print('❌ failed marking as done: ', record_id)

                    time.sleep(5)

                time.sleep(1)
            else:
                print('🚀 fetching from lark...')

                records = self.bitable_manager.get_records(
                    table_id=self.bubble_table_id,
                    filter="OR(CurrentValue.[status] = \"\", CurrentValue.[status] = \"failed\")"
                )

                self.enqueue_pending_records(records)
                
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

    def process_quote_translation_record(self, record):
        retries = 0
        max_retries = 3
        backoff = 3

        while retries < max_retries:
            try:
                if retries > 0:
                    print(f'retrying in {backoff} seconds...')

                audio_url = record['audio_url']
                user_id = record["user_id"]
                email = record["email"]
                given_transcription = record["given_transcription"]

                filename = os.path.join('storage', 'quote_translation', f"{user_id}-{email}.mp3")

                # download the mp3 file
                is_downloaded = self.download_mp3(audio_url, filename)

                if is_downloaded:
                    print('📜 transcribing...')
                    speaker_transcription = self.transcriber.transcribe_with_timestamp(filename)
                    
                    print('⚖️  evaluating quote translation...')
                    evaluation_result = self.eloquent.evaluate_quote_translation(
                        quote=given_transcription,
                        transcription=speaker_transcription
                    )

                    # add audio path
                    evaluation_result["audio_path"] = filename

                    return evaluation_result
                else:
                    retries += 1
                    backoff *= retries
                    time.sleep(backoff)

            except Exception as err:
                print("Error processing: ", err)
                retries += 1
                backoff *= retries
                time.sleep(backoff)
        # skipped this record
        self.skipped_records.append(record['record_id'])

    def process_script_reading_record(self, record):
        retries = 0
        max_retries = 3
        backoff = 3

        while retries < max_retries:
            try:
                if retries > 0:
                    print(f'retrying in {backoff} seconds...')

                audio_url = record['audio_url']
                user_id = record["user_id"]
                email = record["email"]
                given_transcription = record["given_transcription"]

                filename = os.path.join('storage', 'script_reading', f"{user_id}-{email}-{time.time()}.mp3")

                # download the mp3 file
                is_downloaded = self.download_mp3(audio_url, filename)

                if is_downloaded:
                    print('📜 transcribing...')
                    speaker_transcription = self.transcriber.transcribe_with_google(filename)
                    
                    print('⚖️  evaluating script reading...')
                    evaluation_result = self.eloquent.perform_all_evaluation(
                        audio_path=filename,
                        given_script=given_transcription,
                        transcription=speaker_transcription
                    )

                    return evaluation_result
                else:
                    retries += 1
                    backoff *= retries
                    time.sleep(backoff)

            except Exception as err:
                print("Error processing: ", err)
                retries += 1
                backoff *= retries
                time.sleep(backoff)
        # skipped this record
        self.skipped_records.append(record['record_id'])


    def download_mp3(self, url, file_name):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as err:
            return False

if __name__ == '__main__':
    load_dotenv('.env') 

    worker = Worker()

    worker.work()

    

    

    