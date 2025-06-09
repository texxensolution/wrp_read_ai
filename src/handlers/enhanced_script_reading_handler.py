import time
import librosa
import requests
import os
import lark_oapi as lark
import json
from src.common import AppContext, AudioProcessor, TextPreprocessor, \
    TranscriptionProcessor, FeatureExtractor, get_total_word_correct
from src.common.utilities import download_mp3, delete_file, \
    get_necessary_fields_from_payload, log_execution_time
from uuid import uuid4
from src.exceptions import FileUploadError, EvaluationFailureError, \
    AudioIncompleteError
from typing import Dict
from src.dtos import ESRecordingRelatedFieldsScore, EnhancedScriptReadingResultDTO
from src.interfaces import CallbackHandler
from src.tools.message_card_template_helper import (
    enhanced_reading_notification_template_card,
    EnhancedReadingTemplateVariables
)


class EnhancedScriptReadingHandler(CallbackHandler):
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def aggregate_applicant_score(
        self,
        transcription: str,
        given_transcription: str,
        recording_duration: float
    ) -> ESRecordingRelatedFieldsScore:

        words_per_minute = AudioProcessor.calculate_words_per_minute(
            transcription,
            recording_duration
        )

        similarity_score = TranscriptionProcessor.cosine_text_similarity(transcription, given_transcription)

        return ESRecordingRelatedFieldsScore(
            similarity_score=similarity_score,
            words_per_minute=words_per_minute
        )
    
    def calculate_similarity_score(self, partial_fields: ESRecordingRelatedFieldsScore):
        similarity_norm = partial_fields.similarity_score / 5
        overall_score = (
            (similarity_norm) 
        ) * 100                            

        return round(overall_score,None)  

    async def handle(self, payload: Dict[str, str]):
        with log_execution_time() as _:
            generated_filename = None  # Initialize generated_filename
            try:
                process_start = time.time()
                self._ctx.logger.info('enhanced script reading evaluation...')
                # Extract fields from the payload
                fields = get_necessary_fields_from_payload(payload)
                given_transcription = TextPreprocessor.normalize(fields.given_transcription)  # Use the value retrieved from the payload

                # Generate the filename
                generated_filename = os.path.join(
                    'storage',
                    'enhanced_script_reading',   
                    f"{fields.user_id}.{uuid4()}.mp3"
                )

                # Log the generated filename
                self._ctx.logger.info(f"Generated Filename: {generated_filename}")

                # Download the audio file
                self._ctx.logger.info(f"Downloading audio file from: {fields.audio_url}")
                download_mp3(fields.audio_url, generated_filename)

                # Check if the audio file exists
                if not os.path.exists(generated_filename):
                    self._ctx.logger.error(f"Audio file not found: {generated_filename}")
                    await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="invalid audio url"
                    )
                    raise FileNotFoundError(f"Audio file not found: {generated_filename}")

                # # Remove silence and calculate duration
                self._ctx.logger.info('Removing Timestamps from the audio...')
                AudioProcessor.cut_and_merge_say_phrases(generated_filename)

                # self._ctx.logger.info('Removing silence from audio...')
                recording_duration = AudioProcessor.remove_silence_from_audio(generated_filename)
                self._ctx.logger.info(f"Recording duration: {recording_duration} seconds")


                file_token = await self._ctx.file_manager.upload_async(
                                generated_filename
                            )

                # Check for short audio duration
                if recording_duration < 20:
                    raise AudioIncompleteError(
                        name=fields.name,
                        audio_path=generated_filename,
                        message="Audio file is less than 20 seconds."
                    )

                # Proceed with transcription and further processing
                transcription = await self._ctx.transcription_service.transcribe(
                    audio_path=generated_filename,
                    client="groq",
                    model="distil-whisper-large-v3-en",
                    language='en'
                )

                transcription = TextPreprocessor.normalize(transcription)
                # get total correct word count and base word count
                correct_word_count, base_words_count = get_total_word_correct(
                    given_transcription,
                    transcription
                )

                self._ctx.logger.info('calculating similarity score...')

                partial_fields_score = self.aggregate_applicant_score(
                    transcription,
                    given_transcription,
                    recording_duration
                )

                accuracy_score = self.calculate_similarity_score(partial_fields_score)

                llm_response = await self._ctx.script_reading_service.evaluate(
                    transcription=transcription,
                    given_script=given_transcription,
                )


                self._ctx.logger.info('building payload...')

                process_time = time.time() - process_start
                esr_payload = EnhancedScriptReadingResultDTO(
                    name=fields.name,
                    email=fields.email,
                    transcription=transcription,
                    given_transcription=given_transcription,
                    script_id=fields.script_id,
                    evaluation=llm_response.evaluation,
                    audio=file_token,
                    parent_record_id=fields.record_id,
                    correct_word_count=correct_word_count,
                    total_word_count=base_words_count,
                    similarity_score=round(accuracy_score),
                    version=self._ctx.version.upper(),
                    environment=self._ctx.environment.upper()
                )

                lark_stored_response = await self._ctx.stores \
                    .sr_eval_store \
                    .create(
                        esr_payload
                        )

                # update status on lark base
                await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="done"
                )

                self._ctx.logger.info("updating score on bubble database...")

                # update applicant data on bubble database
                # response = await self._ctx.bubble_http_client_service \
                #     .update_reading_score(
                #         fields.record_id,
                #         actual_score
                #     )

                # self._ctx.logger.info(
                #     "bubble request status: %s",
                #     response['status']
                # )

                # get the stored record with shared url
                found_record = await self._ctx.stores \
                    .sr_eval_store \
                    .find_record(
                        record_id=lark_stored_response.data.record.record_id
                    )

                record_content = json.loads(
                    found_record.raw.content.decode()
                )
                

                shared_url = record_content['data']['record']['record_url']
                similarity_score = round((((partial_fields_score.similarity_score / 5) * 100) * .3),None)

                # notify the group chat
                notification_payload = EnhancedReadingTemplateVariables(
                    calculated_score=accuracy_score,
                    correct_word_count=correct_word_count,
                    total_words_count=base_words_count,
                    name=fields.name,
                    view_link=shared_url,
                    evaluation=llm_response.evaluation,
                    similarity_score=round(accuracy_score)
                )

                notif_payload = enhanced_reading_notification_template_card(
                    notification_payload
                )

                await self._ctx.lark_messenger \
                    .send_message_card_to_group_chat(
                        os.getenv("SR_GROUP_CHAT_ID"),
                        notif_payload
                    )

                self._ctx.logger.info(
                    'done processing: %s, processing_time: %s',
                    fields.name,
                    process_time
                )

            except requests.exceptions.InvalidURL as err:
                await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="invalid audio url"
                )
                self._ctx.logger.error(
                    "applicant name: %s, message: %s",
                    fields.name,
                    err
                )

            except FileUploadError as err:
                self._ctx.logger.error(err)

            except AudioIncompleteError:
                await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="audio_less_than_20_secs"
                )
                self._ctx.logger.error(
                    "applicant name: %s, message: audio is less than 20 secs",
                    fields.name
                )

            except EvaluationFailureError as err:
                count = await self._ctx.stores.bubble_data_store.increment_retry(
                    record_id=fields.record_id,
                    count=fields.no_of_retries
                )
                self._ctx.logger.error("evaluation failure: %s", err)

            except requests.exceptions.RequestException as err:
                await self._ctx.stores.bubble_data_store.increment_retry(
                    record_id=fields.record_id,
                    count=fields.no_of_retries
                )
                self._ctx.logger.error("request exception: %s", err)
            
            except KeyError as err:
                await self._ctx.stores.bubble_data_store \
                    .update_status(
                        fields.record_id,
                        "script error"
                    )
                self._ctx.logger.error("error: %s", err)

            except Exception as err:
                self._ctx.logger.error(err)
                await self._ctx.stores.bubble_data_store.increment_retry(
                    record_id=fields.record_id,
                    count=fields.no_of_retries
                )

            finally:
                if generated_filename and os.path.exists(generated_filename):
                    print(generated_filename)
                    delete_file(generated_filename)
                self._ctx.logger.info("delaying for 3 secs...")