import pytest
from io import StringIO
import builtins

import utf_typecase.banner as banner


@pytest.fixture
def capture_print(monkeypatch):
    output = StringIO()
    monkeypatch.setattr(
        builtins, "print", lambda s="", *a, **kw: output.write(str(s) + "\n")
    )
    return output


def test_print_banner_runs_without_error(capture_print):
    sample = "Line1\nLine2 is quite long and should wrap nicely"
    banner.print_banner(sample, padding=4, align="left")
    result = capture_print.getvalue()
    assert "Line1" in result


def test_print_banner_for_known_release(capture_print):
    banner.print_banner_for_release("v0.2.0", padding=2, align="center")
    result = capture_print.getvalue()
    assert "utf-typecase v0.2.0" in result


def test_print_banner_for_unknown_release(capture_print):
    banner.print_banner_for_release("v9.9.9")
    result = capture_print.getvalue()
    assert "🚫 No banner found for release 'v9.9.9'" in result


def test_banner_alignment_left(capture_print):
    banner.print_banner("Hello World", padding=2, align="left")
    result = capture_print.getvalue()
    first_line = result.splitlines()[0]
    assert first_line.startswith("  Hello World")


def test_banner_alignment_right(capture_print):
    banner.print_banner("Hello Right", padding=2, align="right")
    result = capture_print.getvalue()
    first_line = result.splitlines()[0]
    assert first_line.endswith("Hello Right")


def test_banner_alignment_center(capture_print):
    banner.print_banner("Hello Center", padding=2, align="center")
    result = capture_print.getvalue()
    first_line = result.splitlines()[0]
    assert "Hello Center" in first_line
