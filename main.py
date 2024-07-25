import asyncio
import argparse
from src.enums import AssessmentType
from src.common import AppContext, Worker
from src.configs import context
from src.tasks.photo_interpretation_process_callback import photo_interpretation_process_callback
from src.tasks.quote_translation_process_callback import quote_translation_process_cb
from src.tasks.script_reading_process_callback import script_reading_process_cb


def choose_task(server_task: str) -> str:
    if server_task == 'sr':
        return "Script Reading"
    elif server_task == 'quote':
        return "Quote Translation"
    elif server_task == 'photo':
        return "Photo Translation"
    
async def main(server_task: str, ctx: AppContext, worker: Worker):
    should_exit = False

    await ctx.stores.reference_store.sync_and_store_df_in_memory()

    await worker.sync()

    ctx.logger.info('queue count: %s', ctx.task_queue.remaining())

    while not should_exit:
        try:
            if not ctx.task_queue.is_empty():
                ctx.logger.info('queue count: %s', ctx.task_queue.remaining())
                task = ctx.task_queue.pop()
                payload = task.payload
                assessment_type = task.type

                if assessment_type == server_task:
                    if assessment_type == AssessmentType.SCRIPT_READING:
                        await script_reading_process_cb(ctx, payload)
                    elif assessment_type == AssessmentType.PHOTO_TRANSLATION:
                        await photo_interpretation_process_callback(ctx, payload)
                    elif assessment_type == AssessmentType.QUOTE_TRANSLATION:
                        await quote_translation_process_cb(ctx, payload)
            else:
                await worker.sync()
                await asyncio.sleep(3)
            await asyncio.sleep(0.01)
        except KeyboardInterrupt:
            should_exit = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ReadAI Background processor')
    parser.add_argument('--server-task', type=str, default='sr', choices=['sr', 'quote', 'photo'], help='Choose which task to run')
    
    args = parser.parse_args()

    server_task = choose_task(args.server_task)
    print("Server task:", server_task)

    worker = Worker(context)

    asyncio.run(main(server_task, context, worker))

