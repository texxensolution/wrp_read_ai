from modules.whisper import Transcriber

transcriber = Transcriber()

def enqueue_evaluation(applicant_id, audio_path, callback_url):
    # transcription = transcriber.transcribe_with_timestamp(audio_path)

    print(applicant_id, audio_path, callback_url)

def test_queued_func():
    print("hello, world")
    return "hello, world"