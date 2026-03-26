import pytest

from interview_bot.groq_client import GroqLLM


def test_extract_json_full_text():
    assert GroqLLM._extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_embedded_object():
    s = "Here you go:\n\n```json\n{\"a\": 2}\n```"
    assert GroqLLM._extract_json(s) == {"a": 2}


def test_extract_json_embedded_array():
    s = "Result: [1,2,3] thanks"
    assert GroqLLM._extract_json(s) == [1, 2, 3]


def test_extract_json_failure():
    with pytest.raises(ValueError):
        GroqLLM._extract_json("no json here")


