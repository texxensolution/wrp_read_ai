import os
import time
from uuid import uuid4
import requests.exceptions
from src.common import AppContext
from typing import Dict
from src.common.utilities import get_necessary_fields_from_payload, download_mp3, delete_file
from src.dtos import QuoteTranslationResultDTO
from src.interfaces import CallbackHandler

class QuoteTranslationHandler(CallbackHandler):
    def __init__(self, _ctx: AppContext):
        self._ctx = _ctx
    
    def calculate_score(self, understanding: int, insightfulness: int, personal_application: int, personal_connection: int):
        return understanding + insightfulness + personal_application + personal_connection

    async def handle(self, payload: Dict[str, str]):
        self._ctx.logger.info('quote translation processing...')
        process_start = time.time()

        fields = get_necessary_fields_from_payload(payload)

        generated_filename = os.path.join('storage', 'quote_translation', f"{fields.user_id}-{uuid4()}.mp3")

        try:
            self._ctx.logger.info('downloading mp3...')
            download_mp3(fields.audio_url, generated_filename)

            self._ctx.logger.info('transcribing...')
            transcription = await self._ctx.transcription_service.transcribe(generated_filename, "groq")
            _, given_transcription, __ = self._ctx.stores.reference_store.get_record(fields.script_id)

            self._ctx.logger.info('evaluating...')
            result = await self._ctx.quote_translation_service.evaluate(transcription, quote=given_transcription)

            file_token = await self._ctx.file_manager.upload_async(generated_filename)

            processing_time = time.time() - process_start

            payload = QuoteTranslationResultDTO(
                environment=self._ctx.environment.upper(),
                version=self._ctx.version,
                transcription=transcription,
                parent_record_id=fields.record_id,
                quote=given_transcription,
                evaluation=result.get_feedback(),
                audio=file_token,
                name=fields.name,
                email=fields.email,
                processing_time=processing_time,
                insightfulness=result.insightfulness.score,
                personal_connection=result.personal_connection.score,
                practical_application=result.practical_application.score,
                understanding=result.understanding.score
            )

            actual_score = self.calculate_score(
                understanding=result.understanding.score,
                insightfulness=result.insightfulness.score,
                personal_application=result.personal_connection.score,
                personal_connection=result.personal_connection.score
            )

            await self._ctx.stores.applicant_qt_evaluation_store.create(payload)

            await self._ctx.stores.bubble_data_store.update_status(fields.record_id, "done")
            
            self._ctx.logger.info("updating applicant score on bubble database...")
            response = await self._ctx.bubble_http_client_service.update_quote_score(fields.record_id, actual_score)

            self._ctx.logger.info("bubble http request status: %s", response['status'])

            self._ctx.logger.info("done processing: name = %s, duration = %s", fields.name, processing_time)
        except requests.exceptions.InvalidURL as err:
            await self._ctx.stores.bubble_data_store.update_status(record_id=fields.record_id, status="invalid audio url")
        except Exception as err:
            await self._ctx.stores.bubble_data_store.increment_retry(
                record_id=fields.record_id,
                count=fields.no_of_retries
            )
            self._ctx.logger.error('general error: %s', err)
        finally:
            self._ctx.logger.info('deleting mp3...')
            delete_file(generated_filename)


