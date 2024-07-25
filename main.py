import asyncio
import argparse
from typing import Literal, Dict
from src.configs import initialize_dependencies
from src.enums import AssessmentType
from src.common import AppContext, Worker
from src.configs import context
from src.handlers.quote_translation_process_callback import quote_translation_process_cb
from src.handlers.script_reading_process_callback import ScriptReadingHandler, script_reading_process_cb
from src.interfaces import CallbackHandler

def choose_task(server_task: str):
    if server_task == 'quote':
        return "Quote Translation"
    elif server_task == 'photo':
        return "Photo Translation"
    else:
        return "Script Reading"

async def main(
    server_task: Literal["Script Reading", "Quote Translation", "Photo Translation"],
    ctx: AppContext,
    worker: Worker,
    handlers: Dict[str, CallbackHandler]
):
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
                    await handlers[assessment_type].handle(payload)

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

    initialize_dependencies()

    handlers = {
        AssessmentType.SCRIPT_READING: ScriptReadingHandler(context)
    }

    worker = Worker(context, server_task)

    asyncio.run(main(server_task, context, worker, handlers))
