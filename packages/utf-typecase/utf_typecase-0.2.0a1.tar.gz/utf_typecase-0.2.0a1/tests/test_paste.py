import time
from utf_typecase.paste import Paster


def test_paster_invokes_clipboard_and_hotkey(monkeypatch):
    called_chars = []
    hotkey_calls = []

    # Mock pyperclip.copy
    def mock_copy(char):
        called_chars.append(char)

    # Mock pyautogui.hotkey
    def mock_hotkey(modifier, key):
        hotkey_calls.append((modifier, key))

    monkeypatch.setattr("pyperclip.copy", mock_copy)
    monkeypatch.setattr("pyautogui.hotkey", mock_hotkey)

    characters = ["✓", "∞", "★"]
    paster = Paster(delay_ms=10)
    paster.paste(characters)

    # Wait for thread to complete
    time.sleep(len(characters) * (paster.delay + 0.05))

    assert called_chars == characters
    assert hotkey_calls == [("ctrl", "v")] * len(characters)
