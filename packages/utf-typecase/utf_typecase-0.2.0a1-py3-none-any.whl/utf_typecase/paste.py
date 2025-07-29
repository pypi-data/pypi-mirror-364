# src/utf_typecase/paste.py

import pyautogui
import pyperclip
import threading
import time


class Paster:
    def __init__(self, delay_ms=20):
        self.callback = None
        self.delay = delay_ms / 1000.0

    def on_characters(self, func):
        """Register a function that supplies characters to paste."""
        self.callback = func

    def paste(self, chars):
        """Paste characters one by one using keyboard simulation."""
        if isinstance(chars, str):
            chars = list(chars)
        elif not isinstance(chars, list):
            raise TypeError("Expected string or list of characters.")

        threading.Thread(target=self._paste_chars, args=(chars,), daemon=True).start()

    def _paste_chars(self, chars):
        for c in chars:
            pyperclip.copy(c)  # Copy character to clipboard
            pyautogui.hotkey("ctrl", "v")  # Simulate Ctrl+V to paste
            time.sleep(self.delay)


# For quick testing: run with `python src/utf_typecase/paste.py`
if __name__ == "__main__":
    import sys
    import random

    characters = ["A", "B", "C", "✓", "∞", "★", "G", "H"]  # You can customize this list
    paster = Paster(delay_ms=60)

    print("\n🎯 UTF Paster Demo")
    print(
        "This script will simulate keyboard input to 'paste' characters into your currently focused window."
    )
    print("Each character will be typed out one-by-one using virtual keystrokes.\n")

    print("🧪 The characters to be pasted are:")
    print("   " + " ".join(characters) + "\n")

    print("🚨 To avoid accidental execution, please complete the safety check below.")
    print("You’ll be shown a random two-digit number.")
    print("Enter it exactly to confirm you're focused and ready.")
    print("After confirmation, a 5-second countdown will begin —")
    print(
        "so you’ll have time to move your cursor into a safe input field (e.g., text box, document).\n"
    )

    code = random.randint(10, 99)
    print(f"🔐 Safety Check — Enter the number {code} to continue.")
    try:
        entered = input("→ Enter number: ").strip()
        if entered != str(code):
            print("❌ Incorrect input. Paste cancelled.")
            sys.exit(1)

        print("\n⏳ Countdown begins. Move your cursor now!")
        for i in reversed(range(1, 6)):
            print(f"   {i}...")
            time.sleep(1)

        paster.paste(characters)
        print("\n✅ Characters are being pasted now. Watch your input field!")

        # Optional wait to keep script alive until paste finishes
        time.sleep(len(characters) * (paster.delay + 1))

    except KeyboardInterrupt:
        paster.cancel()
        print("👋 Paste cancelled by user.")
        sys.exit(0)
