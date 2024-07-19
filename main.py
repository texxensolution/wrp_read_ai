import asyncio
from src.enums import AssessmentType
from src.common import AppContext, Worker
from config import ctx
from src.tasks.quote_translation_process_callback import quote_translation_process_cb
from src.tasks.script_reading_process_callback import script_reading_process_cb

async def main(ctx: AppContext, worker: Worker):
    should_exit = False

    await worker.sync()

    ctx.logger.info('queue count: %s', ctx.task_queue.remaining())

    while not should_exit:
        try:
            if not ctx.task_queue.is_empty():
                ctx.logger.info('queue count: %s', ctx.task_queue.remaining())
                task = ctx.task_queue.pop()
                payload = task.payload
                assessment_type = task.type

                print(ctx.server_task)

                if assessment_type in ctx.server_task:
                    if assessment_type == AssessmentType.SCRIPT_READING:
                        await script_reading_process_cb(ctx, payload)
                    elif assessment_type == AssessmentType.PHOTO_TRANSLATION:
                        pass
                    elif assessment_type == AssessmentType.QUOTE_TRANSLATION:
                        await quote_translation_process_cb(ctx, payload)
            else:
                await worker.sync()
                await asyncio.sleep(3)
            await asyncio.sleep(0.01)
        except KeyboardInterrupt:
            should_exit = True

if __name__ == "__main__":
    worker = Worker(ctx)
    asyncio.run(main(ctx, worker))

