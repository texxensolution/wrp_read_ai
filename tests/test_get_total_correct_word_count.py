import pytest
from src.common import get_total_word_correct

@pytest.mark.parametrize(
    "base_text, given_script, expected_result",
    [
        pytest.param("hello world nice one", "hello world nice one one", (4, 4), id="test_correct_word_count_without_pentalty"),
        pytest.param("hello world nice one one two three", "hello world nice one one", (5, 7), id="test_correct_word_count_five_over_seven"),
        pytest.param("hello world nice one one two three", "", (0, 7), id="test_correct_word_count_zero"),
        pytest.param("", "test", (0, 0), id="test_correct_word_count_zero")
    ]
)
def test_correct_word_count(base_text: str, given_script: str, expected_result):
    assert get_total_word_correct(base_text, given_script) == expected_result