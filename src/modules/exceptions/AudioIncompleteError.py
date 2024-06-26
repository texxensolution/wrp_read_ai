class AudioIncompleteError(Exception):
    def __init__(self, name: str, audio_path: str, message="Audio file is incomplete"):
        self.message = message
        self.name = name
        self.audio_path = audio_path
        super().__init__(f"PartialAudioError: name={self.name}, message={self.message}, audio_path={audio_path}")
