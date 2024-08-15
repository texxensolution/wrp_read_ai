import asyncio
import argparse
from typing import Dict
from src.configs.initialize_dependencies import initialize_dependencies
from src.enums import AssessmentType
from src.common import AppContext, Worker
from src.configs.setup_context import context
from src.interfaces import CallbackHandler
from src.handlers import QuoteTranslationHandler, ScriptReadingHandler

Handlers = Dict[str, CallbackHandler]


async def main(
    server_task: str,
    ctx: AppContext,
    worker: Worker,
    handlers: Handlers
):
    """
        Entry point:
        1. This will setup all necessary dependencies and fetch all references 
        from lark base
        2. This will create an infinite loop that will poll and process 
        assessment dynamically based on their assessment types
    """
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
            ctx.logger.info("delay for 1 sec...")
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            should_exit = True

if __name__ == "__main__":
    print("starting...")
    parser = argparse.ArgumentParser(description='ReadAI Background processor')
    parser.add_argument(
        '--server-task',
        type=str,
        default='sr',
        choices=['sr', 'quote', 'photo'],
        help='Choose which task to run'
    )

    args = parser.parse_args()

    task_map = {
        "sr": AssessmentType.SCRIPT_READING,
        "quote": AssessmentType.QUOTE_TRANSLATION,
    }

    # map shortcut name to its real name
    server_task = task_map[args.server_task]

    print("Server task:", server_task)

    initialize_dependencies()

    # map handlers for all supported assessments
    handlers: Handlers = {
        AssessmentType.SCRIPT_READING: ScriptReadingHandler(context),
        AssessmentType.QUOTE_TRANSLATION: QuoteTranslationHandler(context)
    }

    worker = Worker(context, server_task)

    asyncio.run(main(server_task, context, worker, handlers))
