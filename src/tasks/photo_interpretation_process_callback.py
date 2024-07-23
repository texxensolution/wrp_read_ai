import os
import time
from uuid import uuid4
import requests
from src.common.utilities import get_necessary_fields_from_payload, download_mp3
from typing import Dict
from src.common import AppContext
from src.dtos import PhotoInterpretationResultDTO


def make_sure_to_have_necessary_folders():
    path = os.path.join('storage', 'photo_interpretation')

    if not os.path.exists(path):
        os.makedirs(path)
async def photo_interpretation_process_callback(ctx: AppContext, payload: Dict[str, str]):
    ctx.logger.info('photo interpretation evaluating...')
    process_start = time.time()

    make_sure_to_have_necessary_folders()

    fields = get_necessary_fields_from_payload(payload)

    generated_filename = os.path.join('storage', 'photo_interpretation', f"{fields.email}-{uuid4()}.mp3")

    make_sure_to_have_necessary_folders()

    try:
        ctx.logger.info('downloading mp3...')
        download_mp3(fields.audio_url, generated_filename)

        ctx.logger.info('transcribing...')
        transcription = await ctx.transcription_service.transcribe(generated_filename, "groq")
        _, description, __ = ctx.stores.reference_store.get_record(fields.script_id)

        ctx.logger.info('evaluating...')
        result = await ctx.photo_interpretation_service.evaluate(transcription, description=description)

        file_token = await ctx.file_manager.upload_async(generated_filename)

        processing_time = time.time() - process_start

        payload = PhotoInterpretationResultDTO(
            environment=ctx.environment.upper(),
            version=ctx.version,
            transcription=transcription,
            parent_record_id=fields.record_id,
            description=description,
            evaluation=result.evaluation,
            analytical_thinking=result.analytical_thinking,
            originality=result.originality,
            language=result.language,
            support=result.support,
            organization=result.organization,
            focus_point=result.focus_point,
            audio=file_token,
            name=fields.name,
            email=fields.email,
            processing_time=processing_time
        )

        await ctx.stores.applicant_photo_evaluation_store.create(payload)

        await ctx.stores.bubble_data_store.update_status(fields.record_id, "done")

        ctx.logger.info("done processing: name = %s, duration = %s", fields.name, processing_time)
    except requests.exceptions.InvalidURL as err:
        await ctx.stores.bubble_data_store.update_status(record_id=fields.record_id, status="invalid audio url")
    except Exception as err:
        await ctx.stores.bubble_data_store.increment_retry(
            record_id=fields.record_id,
            count=fields.no_of_retries
        )
        ctx.logger.error('general error: %s', err)

