import time
import librosa
import requests
import os
import json
from src.common import AppContext, AudioProcessor, TextPreprocessor, TranscriptionProcessor, \
FeatureExtractor, get_total_word_correct
from src.common.utilities import download_mp3, delete_file, get_necessary_fields_from_payload, log_execution_time
from uuid import uuid4
from src.exceptions import FileUploadError, EvaluationFailureError, AudioIncompleteError
from speech_recognition.exceptions import TranscriptionFailed
from typing import Dict
from src.dtos import RecordingRelatedFieldsScore, ScriptReadingResultDTO
from src.interfaces import CallbackHandler
from src.tools.message_card_template_helper import reading_notification_template_card, ReadingTemplateVariables

class ScriptReadingHandler(CallbackHandler):
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def aggregate_applicant_score(
        self,
        generated_filename: str,
        transcription: str,
        given_transcription: str,
        recording_duration: float
    ) -> RecordingRelatedFieldsScore:

        y, sr = librosa.load(generated_filename, sr=16000)
        avg_pause_duration = FeatureExtractor(y, sr).calculate_pause_duration()
        words_per_minute = AudioProcessor.calculate_words_per_minute(transcription, recording_duration)
        wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
        pronunciation, fluency = self._ctx.voice_analyzer_service.calculate_score(generated_filename)
        similarity_score = TranscriptionProcessor.compute_distance(transcription, given_transcription)
        pacing_score = AudioProcessor.determine_speaker_pacing(words_per_minute, avg_pause_duration)

        return RecordingRelatedFieldsScore(
            fluency=fluency,
            avg_pause_duration=avg_pause_duration,
            pronunciation=pronunciation,
            wpm_category=wpm_category,
            similarity_score=similarity_score,
            pacing_score=pacing_score,
            words_per_minute=words_per_minute
        )
    
    def calculate_score(self, partial_fields: RecordingRelatedFieldsScore):
        return round(
            (
                ((partial_fields.pronunciation / 5) * .25) +
                ((partial_fields.wpm_category) / 5) * .15 +
                ((partial_fields.similarity_score / 5)) * .20 +
                ((partial_fields.fluency / 5) * .25) + 
                ((partial_fields.pacing_score / 5) * .15)
            ) * 100
        )

    async def handle(self, payload: Dict[str, str]):
        with log_execution_time() as get_elapsed_time:
            try:
                process_start = time.time()
                self._ctx.logger.info('script reading evaluation...')

                fields = get_necessary_fields_from_payload(payload)

                given_transcription = self._ctx.stores.reference_store.get_script(fields.script_id)

                generated_filename = os.path.join('storage', 'script_reading', f"{fields.user_id}.{uuid4()}.mp3")

                self._ctx.logger.info('downloading audio url from %s', fields.audio_url)
                download_mp3(fields.audio_url, generated_filename)

                self._ctx.logger.info('removing silence from audio...')
                recording_duration = AudioProcessor.remove_silence_from_audio(generated_filename)

                file_token = await self._ctx.file_manager.upload_async(generated_filename)

                if recording_duration < 30:
                    raise AudioIncompleteError(
                        name=fields.name,
                        audio_path=generated_filename,
                        message="Audio file is less than 30 secs."
                    )

                self._ctx.logger.info('transcribing...')
                transcription = await self._ctx.transcription_service.transcribe(generated_filename)
                transcription = TextPreprocessor.normalize(transcription)

                # get total correct word count and base word count
                correct_word_count, base_words_count = get_total_word_correct(given_transcription, transcription)

                self._ctx.logger.info('calculating similarity score...')

                partial_fields_score = self.aggregate_applicant_score(
                    generated_filename,
                    transcription,
                    given_transcription,
                    recording_duration
                )

                actual_score = self.calculate_score(partial_fields_score)

                llm_response = await self._ctx.script_reading_service.evaluate(
                    transcription=transcription,
                    given_script=given_transcription
                )

                self._ctx.logger.info('building payload...')

                process_time = time.time() - process_start

                sr_payload = ScriptReadingResultDTO(
                    name=fields.name,
                    email=fields.email,
                    transcription=transcription,
                    given_transcription=given_transcription,
                    script_id=fields.script_id,
                    evaluation=llm_response.evaluation,
                    audio=file_token,
                    fluency=partial_fields_score.fluency,
                    similarity_score=partial_fields_score.similarity_score,
                    pronunciation=partial_fields_score.pronunciation,
                    pacing_score=partial_fields_score.pacing_score,
                    wpm_category=partial_fields_score.wpm_category,
                    parent_record_id=fields.record_id,
                    audio_duration_seconds=recording_duration,
                    words_per_minute=partial_fields_score.words_per_minute,
                    correct_word_count=correct_word_count,
                    total_word_count=base_words_count,
                    processing_duration=process_time,
                    avg_pause_duration=partial_fields_score.avg_pause_duration,
                    version=self._ctx.version.upper(),
                    environment=self._ctx.environment.upper()
                )

                lark_stored_response = await self._ctx.stores.applicant_sr_evaluation_store.create(sr_payload)

                # update status on lark base
                await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="done"
                )

                self._ctx.logger.info("updating score on bubble database...")

                # update applicant data on bubble database
                response = await self._ctx.bubble_http_client_service.update_reading_score(fields.record_id, actual_score)
                self._ctx.logger.info("bubble request status: %s", response['status'])

                found_record = await self._ctx.stores.applicant_sr_evaluation_store.find_record(
                    record_id=lark_stored_response.data.record.record_id
                )

                found_record_content = json.loads(found_record.raw.content.decode())

                shared_url = found_record_content['data']['record']['record_url']

                # notify the group chat
                notification_payload = ReadingTemplateVariables(
                    calculated_score=actual_score,
                    voice_quality=partial_fields_score.pronunciation,
                    pacing_score=partial_fields_score.pacing_score,
                    wpm_category=partial_fields_score.wpm_category,
                    fluency_score=partial_fields_score.fluency,
                    accuracy_score=partial_fields_score.similarity_score,
                    correct_count=correct_word_count,
                    total_words_count=base_words_count,
                    name=fields.name,
                    view_link=shared_url,
                    given_script=fields.given_transcription,
                    evaluation=llm_response.evaluation
                )

                notif_payload = reading_notification_template_card(notification_payload)

                await self._ctx.lark_messenger.send_message_card_to_group_chat(
                    os.getenv("SR_GROUP_CHAT_ID"),
                    notif_payload
                )

                self._ctx.logger.info('done processing: %s, processing_time: %s', fields.name, process_time)

            except requests.exceptions.InvalidURL as err:
                await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="invalid audio url"
                )
                self._ctx.logger.error("applicant name: %s, message: %s", fields.name, err)

            except FileUploadError as err:
                self._ctx.logger.error(err)

            except AudioIncompleteError as err:
                await self._ctx.stores.bubble_data_store.update_status(
                    record_id=fields.record_id,
                    status="audio_less_than_30_secs"
                )
                self._ctx.logger.error("applicant name: %s, message: audio is less than 30 secs", fields.name)

            except TranscriptionFailed as err:
                await self._ctx.stores.bubble_data_store.increment_retry(
                    record_id=fields.record_id,
                    count=fields.no_of_retries
                )
                self._ctx.logger.error("transcription failure: %s", err)

            except EvaluationFailureError as err:
                await self._ctx.stores.bubble_data_store.increment_retry(
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
                await self._ctx.stores.bubble_data_store.update_status(fields.record_id, "script error")
                self._ctx.logger.error("error: %s", err)

            except Exception as err:
                self._ctx.logger.error(err)
                await self._ctx.stores.bubble_data_store.increment_retry(
                    record_id=fields.record_id,
                    count=fields.no_of_retries
                )

            finally:
                if generated_filename and os.path.exists(generated_filename):
                    delete_file(generated_filename)
                self._ctx.logger.info("delaying for 3 secs...")