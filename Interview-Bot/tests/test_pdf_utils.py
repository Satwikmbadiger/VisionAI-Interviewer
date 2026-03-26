from pathlib import Path

from interview_bot.pdf_utils import clip_text, normalize_text


def test_normalize_text_collapses_whitespace():
    s = "Hello\t\tworld \n\n\nThis   is  a test\r\n\r\nDone"
    out = normalize_text(s)
    assert "  " not in out
    assert "\n\n\n" not in out
    assert "Hello world" in out


def test_clip_text():
    assert clip_text("abc", 2) == "ab"
    assert clip_text("abc", 3) == "abc"
    assert clip_text("abc", 0) == ""


