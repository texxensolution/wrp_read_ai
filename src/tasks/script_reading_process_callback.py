import time

import librosa
import requests
import os
from src.common import AppContext, AudioConverter, AudioProcessor, TextPreprocessor, TranscriptionProcessor, \
    FeatureExtractor
from src.common.utilities import download_mp3, delete_file
from uuid import uuid4

from src.enums import BubbleRecordStatus
from src.exceptions import FileUploadError, EvaluationFailureError, AudioIncompleteError
from speech_recognition.exceptions import TranscriptionFailed
from typing import Dict
from src.dtos import RequiredFieldsScriptReading, RecordingRelatedFieldsScore, ScriptReadingResultDTO


def get_necessary_fields_from_payload(payload: Dict[str, str]):
    user_id = payload['user_id']
    email = payload['email']
    record_id = payload['record_id']
    audio_url = payload['audio_url']
    script_id = payload['script_id']
    name = payload['name']
    no_of_retries = payload['no_of_retries']

    return RequiredFieldsScriptReading(
        name=name,
        record_id=record_id,
        user_id=user_id,
        email=email,
        audio_url=audio_url,
        script_id=script_id,
        no_of_retries=no_of_retries
    )


def generate_filename(email: str):
    return f"{email}-{uuid4()}.mp3"


def calculate_applicant_score(
    ctx: AppContext,
    generated_filename: str,
    transcription: str,
    given_transcription: str,
    recording_duration: float
) -> RecordingRelatedFieldsScore:

    y, sr = librosa.load(generated_filename, sr=16000)
    avg_pause_duration = FeatureExtractor(y, sr).calculate_pause_duration()
    words_per_minute = AudioProcessor.calculate_words_per_minute(transcription, recording_duration)
    wpm_category = AudioProcessor.determine_wpm_category(words_per_minute)
    pronunciation, fluency = ctx.voice_analyzer_service.calculate_score(generated_filename)
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


async def script_reading_process_cb(ctx: AppContext, payload: Dict[str, str]):
    ctx.logger.info('script reading evaluation...')
    process_start = time.time()

    fields = get_necessary_fields_from_payload(payload)

    given_transcription = ctx.script_extractor_service.get_script(fields.script_id)

    generated_filename = os.path.join('storage', 'script_reading', generate_filename(fields.email))

    try:
        ctx.logger.info('downloading audio url from %s', fields.audio_url)
        download_mp3(fields.audio_url, generated_filename)

        ctx.logger.info('removing silence from audio...')
        recording_duration = AudioProcessor.remove_silence_from_audio(generated_filename)

        file_token = await ctx.file_manager.upload_async(generated_filename)

        if recording_duration < 30:
            raise AudioIncompleteError(
                name=fields.name,
                audio_path=generated_filename,
                message="Audio file is less than 30 secs."
            )

        ctx.logger.info('transcribing...')
        transcription = await ctx.transcription_service.transcribe(generated_filename)
        transcription = TextPreprocessor.normalize(transcription)

        ctx.logger.info('calculating similarity score...')

        partial_fields_score = calculate_applicant_score(
            ctx,
            generated_filename,
            transcription,
            given_transcription,
            recording_duration
        )

        evaluation = await ctx.llama_service.chat(
            f"""
                Instruction:
                Language: English
                Evaluate the transcription based on the criteria below and give a brief description of how you evaluated the criteria.
                Criteria:
                Compare the Speaker Transcription and Given Script
                Identify mispronunciations between the speaker transcription and given script
                If the speaker transcription is empty, return "Invalid"

                Speaker Transcription: {transcription}
                Given Script: {given_transcription}
                - Dont show any criteria just the evaluation
            """
        )

        ctx.logger.info('building payload...')

        process_time = time.time() - process_start

        sr_payload = ScriptReadingResultDTO(
            name=fields.name,
            email=fields.email,
            transcription=transcription,
            given_transcription=given_transcription,
            script_id=fields.script_id,
            evaluation=evaluation,
            audio=file_token,
            fluency=partial_fields_score.fluency,
            similarity_score=partial_fields_score.similarity_score,
            pronunciation=partial_fields_score.pronunciation,
            pacing_score=partial_fields_score.pacing_score,
            wpm_category=partial_fields_score.wpm_category,
            parent_record_id=fields.record_id,
            audio_duration_seconds=recording_duration,
            words_per_minute=partial_fields_score.words_per_minute,
            processing_duration=process_time,
            avg_pause_duration=partial_fields_score.avg_pause_duration,
            version=ctx.version.upper(),
            environment=ctx.environment.upper()
        )

        await ctx.stores.applicant_sr_evaluation_store.create(sr_payload)

        await ctx.stores.bubble_data_store.update_status(
            record_id=fields.record_id,
            status="done"
        )

        ctx.logger.debug('done processing: %s, processing_time: %s', fields.name, process_time)

    except requests.exceptions.InvalidURL as err:
        await ctx.stores.bubble_data_store.update_status(
            record_id=fields.record_id,
            status="invalid audio url"
        )
        ctx.logger.error("applicant name: %s, message: %s", fields.name, err)

    except FileUploadError as err:
        ctx.logger.error(err)

    except AudioIncompleteError as err:
        await ctx.stores.bubble_data_store.update_status(
            record_id=fields.record_id,
            status="audio_less_than_30_secs"
        )
        ctx.logger.error("applicant name: %s, message: audio is less than 30 secs", fields.name)

    except TranscriptionFailed as err:
        await ctx.stores.bubble_data_store.increment_retry(
            record_id=fields.record_id,
            count=fields.no_of_retries
        )
        ctx.logger.error("transcription failure: %s", err)

    except EvaluationFailureError as err:
        await ctx.stores.bubble_data_store.increment_retry(
            record_id=fields.record_id,
            count=fields.no_of_retries
        )
        ctx.logger.error("evaluation failure: %s", err)

    except requests.exceptions.RequestException as err:
        await ctx.stores.bubble_data_store.increment_retry(
            record_id=fields.record_id,
            count=fields.no_of_retries
        )
        ctx.logger.error("request exception: %s", err)

    except Exception as err:
        ctx.logger.error(err)
        await ctx.stores.bubble_data_store.increment_retry(
            record_id=fields.record_id,
            count=fields.no_of_retries
        )

    finally:
        if generated_filename and os.path.exists(generated_filename):
            delete_file(generated_filename)