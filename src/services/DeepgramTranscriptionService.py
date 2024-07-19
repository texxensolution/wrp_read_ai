import os
from deepgram import DeepgramClient, FileSource, PrerecordedOptions
from src.interfaces import ITranscriber


class DeepgramTranscriptionService(ITranscriber):
    def __init__(self, token=os.getenv('DEEPGRAM_TOKEN')):
        self.deepgram = DeepgramClient(api_key=token)
    
    async def transcribe(self, audio_path: str):
        try:

            with open(audio_path, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
                "buffer": buffer_data,
            }

            #STEP 2: Configure Deepgram options for audio analysis
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=False,
                punctuate=False
            )

            response = await self.deepgram.listen.asyncprerecorded.v("1").transcribe_file(payload, options)

            # STEP 4: Print the response
            return response['results']['channels'][0]['alternatives'][0]['transcript']

        except Exception as e:
            raise Exception("Transcription failed: ", e)