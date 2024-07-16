#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from src.modules.common import (DataTransformer, FluencyAnalysis, LarkQueue,
                                Logger, PronunciationAnalyzer, Task, TaskQueue, ScriptExtractor)
from src.modules.lark import BitableManager, FileManager, Lark
from src.modules.ollama import EloquentOpenAI, Ollama
from src.modules.process import (QuoteTranslationEvaluator,
                                 ScriptReadingEvaluator)
from src.modules.whisper import Transcriber
from src.modules.logger import LarkHandler

@dataclass
class Worker:
    """Worker is responsible for processing applicant submission"""
    load_dotenv()
    task_queue: TaskQueue
    lark_queue: LarkQueue
    script_reader: ScriptReadingEvaluator
    quote_translation: QuoteTranslationEvaluator
    logs: logging.Logger

    def create_storage_folders(self):
        """Create storage folder when running worker.py"""
        script_reading_dir = os.path.join('storage', 'script_reading')
        if not os.path.exists(script_reading_dir):
            os.makedirs(script_reading_dir)

    async def switch_cases(self, task: Task):
        """Customize Switch Case to reduce noise"""
        if task.type == 'Script Reading':
            await self.script_reader.process(task)
        elif task.type == 'Quote Translation':
            self.quote_translation.process(task)

    def sync(self):
        """Synchronize items from lark to TaskQueue"""
        # Get the current date and time
        now = datetime.now()

        # Format the date and time
        formatted_time = now.strftime("%A at %I:%M %p")

        self.logs.info('🔄 syncing from lark at %s', formatted_time)

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
                "status",
                "script_id",
                "no_of_retries"
            ]
        )
        self.task_queue.enqueue_many(transformed_records)

    def calculate_queued_task_display(self, queue_length: int):
        """return the number of applicant queue"""
        human_queue_str = ""
        for i in range(queue_length):
            if i % 2 == 0:
                human_queue_str += "🚶‍♂️"
            else:
                human_queue_str += "🚶‍♀️"
        return human_queue_str + " current applicants waiting at the queue: " + str(queue_length)

    async def processing(self):
        """
            This will 
        """
        self.logs.info("👷 Worker is processing...")

        self.sync()

        while True:
            if not self.task_queue.is_empty():
                queue_length = self.task_queue.remaining()
                queue_display_str = self.calculate_queued_task_display(queue_length)
                self.logs.info(queue_display_str)

                task = self.task_queue.pop()
                name = task.payload['name']
                email = task.payload['email']
                self.logs.info('⚙️  processing: name=%s, email=%s...', name, email)
                await self.switch_cases(task)
            else:
                self.sync()
                await asyncio.sleep(3)

async def main():
    """main initializer"""
    

    info_log_file = os.path.join("worker_info.log")
    error_log_file = os.path.join("worker_error.log")

    # Configure the info file handler to log info and above
    info_handler = RotatingFileHandler(info_log_file, maxBytes=10**6, backupCount=5, encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Configure the error file handler to log only errors
    error_handler = RotatingFileHandler(error_log_file, maxBytes=10**6, backupCount=5, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Configure the stream handler to log all levels to the console
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    lark = Lark(
        app_id=os.getenv("APP_ID"),
        app_secret=os.getenv("APP_SECRET")
    )

    base_manager = BitableManager(
        lark_client=lark,
        bitable_token=os.getenv("BITABLE_TOKEN")
    )

    # # lark logging handler
    # lark_log_handler = LarkHandler(
    #     bitable_manager=base_manager,
    #     log_table_token=os.getenv("LOG_MONITORING_TABLE_ID")
    # )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[info_handler, error_handler, stream_handler]
    )

    environment = os.getenv("ENV")
    version = os.getenv("VERSION")

    logger = logging.getLogger()

    logger.info(f"Environment: %s", environment)
    logger.info(f"Version: %s", version)

    logger.info('loading environment variables...')

    task_queue = TaskQueue()

    lark_queue = LarkQueue(
        base_manager=base_manager,
        bitable_table_id=os.getenv("BUBBLE_TABLE_ID"),
        version=version,
        environment=environment
    )

    file_manager = FileManager(
        lark_client=lark,
        bitable_token=os.getenv('BITABLE_TOKEN')
    )

    logger.info('loading ai models...')

    eloquent = EloquentOpenAI()

    transcriber = Transcriber()

    ollama_client = Ollama('llama3:instruct')

    pronunciation_analyzer = PronunciationAnalyzer()

    fluency_analysis = FluencyAnalysis()

    script_extractor = ScriptExtractor(version=version)

    script_reader = ScriptReadingEvaluator(
        base_manager=base_manager,
        file_manager=file_manager,
        transcriber=transcriber,
        eloquent=eloquent,
        ollama_client=ollama_client,
        fluency_analysis=fluency_analysis,
        script_extractor=script_extractor,
        pronunciation_analyzer=pronunciation_analyzer,
    )

    quote_translation = QuoteTranslationEvaluator(
        file_manager=file_manager,
        base_manager=base_manager,
        openai=eloquent
    )

    worker = Worker(
        task_queue=task_queue,
        lark_queue=lark_queue,
        script_reader=script_reader,
        quote_translation=quote_translation,
        logs=logger
    )
    
    worker.create_storage_folders()

    await worker.processing()

if __name__ == '__main__':
    
    load_dotenv('.env')

    asyncio.run(main())
