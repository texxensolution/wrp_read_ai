import os
import time
import asyncio
from src.modules.lark import Lark, BitableManager, FileManager
from dotenv import load_dotenv
from datetime import datetime
from src.modules.whisper import Transcriber
from src.modules.ollama import EloquentOpenAI
from dataclasses import dataclass
from src.modules.common import TaskQueue, Task, LarkQueue, DataTransformer, Logger, FluencyAnalysis, PronunciationAnalyzer
from src.modules.process import ScriptReadingEvaluator, QuoteTranslationEvaluator

@dataclass
class Worker:
    load_dotenv()
    task_queue: TaskQueue
    lark_queue: LarkQueue 
    script_reader: ScriptReadingEvaluator
    quote_translation: QuoteTranslationEvaluator

    def create_storage_folders(self):
        script_reading_dir = os.path.join('storage', 'script_reading')

        if not os.path.exists(script_reading_dir):
            os.makedirs(script_reading_dir)

    def get_correct_table_id(self, assessment_type: str):
        if assessment_type == "Script Reading":
            return os.getenv('SCRIPT_READING_TABLE_ID')
        elif assessment_type == "Quote Translation":
            return os.getenv('QUOTE_TRANSLATION_TABLE_ID')

    async def switch_cases(self, task: Task):
        if task.type == 'Script Reading':
            await self.script_reader.process(task)
        elif task.type == 'Quote Translation':
            self.quote_translation.process(task)

    def sync(self):
        # Get the current date and time
        now = datetime.now()

        # Format the date and time
        formatted_time = now.strftime("%A at %I:%M %p")

        print(f'🔄 syncing from lark at {formatted_time}')

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
        human_queue_str = ""
        for i in range(queue_length):
            if i % 2 == 0:
                human_queue_str += "🚶‍♂️"
            else:
                human_queue_str += "🚶‍♀️"
        return human_queue_str + " current applicants waiting at the queue: " + str(queue_length)

    async def processing(self):
        print("👷 Worker is processing...")

        self.sync()

        while True:
            if not self.task_queue.is_empty():
                queue_length = self.task_queue.remaining()
                queue_display_str = self.calculate_queued_task_display(queue_length)
                print(queue_display_str)

                task = self.task_queue.pop()
                name = task.payload['name']
                email = task.payload['email']
                print(f'⚙️  processing: name={name}, email={email}...')
                await self.switch_cases(task)
            else:
                self.sync()
                await asyncio.sleep(3)

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
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_datetime

async def main():
    load_dotenv('.env')
    print('initializing queue...')

    task_queue = TaskQueue()

    print('initializing lark envs...')
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

    print('loading ai models...')

    eloquent = EloquentOpenAI()

    transcriber = Transcriber()

    pronunciation_analyzer = PronunciationAnalyzer()

    logs_manager = Logger(
        base_manager=base_manager
    )

    fluency_analysis = FluencyAnalysis()

    script_reader = ScriptReadingEvaluator(
        base_manager=base_manager,
        file_manager=file_manager,
        transcriber=transcriber,
        eloquent=eloquent,
        logs_manager=logs_manager,
        fluency_analysis=fluency_analysis,
        pronunciation_analyzer=pronunciation_analyzer
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
    )
    
    worker.create_storage_folders()

    await worker.processing()

if __name__ == '__main__':
    asyncio.run(main())
