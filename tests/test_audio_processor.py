import pytest
from src.common import AudioProcessor

@pytest.mark.parametrize("wpm, expected_result", [
    pytest.param(161, 4, id="test_wpm_category_returns_four"),
    pytest.param(121, 5, id="test_wpm_category_returns_five"),
    pytest.param(81, 3, id="test_wpm_category_returns_three"),
    pytest.param(15, 2, id="test_wpm_category_returns_two"),
    pytest.param(202, 1, id="test_wpm_category_returns_one")
])
def test_wpm_category_score(wpm, expected_result):
    assert AudioProcessor.determine_wpm_category(wpm) == expected_result

@pytest.mark.parametrize("pitch_std, expected_result", [
    pytest.param(3, 5, id="test_pitch_consistency_score_returns_five"),
    pytest.param(8, 4, id="test_pitch_consistency_score_returns_four"),
    pytest.param(15, 3, id="test_pitch_consistency_score_returns_three"),
    pytest.param(25, 2, id="test_pitch_consistency_score_returns_two"),
    pytest.param(50, 1, id="test_pitch_consistency_score_returns_one"),
])
def test_pitch_consistency_score(pitch_std: float, expected_result: int):
    assert AudioProcessor.determine_pitch_consistency(pitch_std) == expected_result
    