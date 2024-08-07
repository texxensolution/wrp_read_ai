import pytest
from src.common import TranscriptionProcessor 

@pytest.mark.parametrize(
    "transcription, given_script, expected_result",
    [
        pytest.param("hello, world", "goodbye, world", pytest.approx(2.3, abs=9e-2)),
        pytest.param("Hello world", "hello World", pytest.approx(5.0))
    ]
)
def test_transcription_processor(transcription: str, given_script: str, expected_result):
    assert TranscriptionProcessor.compute_distance(transcription, given_script) == expected_result
