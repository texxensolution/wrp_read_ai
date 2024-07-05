from pydub import AudioSegment
from pathlib import Path
import os


class AudioConverter:
    """audio converter class"""
    @staticmethod
    def get_file_path_and_directories(audio_path: str):
        """get the file path, filename, name without extension"""
        path = Path(audio_path)
        directories = path.parent
        basename = path.name
        name_without_extension = path.stem

        return directories, basename, name_without_extension

    @staticmethod
    def convert_mp3_to_wav(audio_path: str):
        """convert mp3 file to wav file"""
        try:
            directories, basename, name_without_extension = AudioConverter.get_file_path_and_directories(audio_path)

            audio: AudioSegment = AudioSegment.from_mp3(audio_path)

            new_filename = os.path.join(directories, f"{name_without_extension}_converted.wav")

            audio.export(new_filename, format='wav')

            return new_filename
        except Exception as err:
            raise Exception(f"Failed to load {basename}: ", err)

    @staticmethod
    def convert_wav_to_mp3(audio_path: str):
        """convert wav file to mp3 file"""
        try:
            _directory, filename = audio_path.rsplit('.wav')

            audio: AudioSegment = AudioSegment.from_wav(audio_path)

            new_filename = f"{filename}.mp3"

            audio.export(new_filename, format='mp3')

            return new_filename
        except Exception as err:
            raise Exception(f"Failed to load {filename}: ", err)