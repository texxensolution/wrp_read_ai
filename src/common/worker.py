import os
from dataclasses import dataclass, asdict
from datetime import datetime

from src.common import (DataTransformer,
                        AppContext)


@dataclass
class Worker:
    """Worker is responsible for processing applicant submission"""

    def __init__(self, ctx: AppContext, server_task: str):
        self._ctx = ctx
        self.server_task = server_task

    def create_storage_folders(self):
        """Create storage folder when running worker.py"""
        script_reading_dir = os.path.join('storage', 'script_reading')
        if not os.path.exists(script_reading_dir):
            os.makedirs(script_reading_dir)

    async def sync(self):
        """Synchronize items from lark to TaskQueue"""
        # Get the current date and time
        now = datetime.now()

        # Format the date and time
        formatted_time = now.strftime("%A at %I:%M %p")

        self._ctx.logger.info('🔄 syncing from lark at %s', formatted_time)

        records = await self._ctx.lark_queue.get_items(self.server_task)

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
        self._ctx.task_queue.enqueue_many(transformed_records)
