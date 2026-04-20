import vosk
import sounddevice as sd
import queue
import json
import pyautogui
import threading
import os
import sys
import time
import webbrowser
from rapidfuzz import fuzz
from PyQt6.QtWidgets import QApplication
from ui import Sphere

PRESENTATION_PASSWORD = "crimson access"
PRESENTATION_PASSWORD_VARIANTS = [
    "crimson access",
    "crimson",
    "crison access",
    "crison",
    "crimon access",
    "crimon",
    "krimson access",
    "krimson",
    "crimzon access",
    "crimzon",
]

PRESENTATION_URL = "https://alpha-chi-henna.vercel.app"

audio_queue = queue.Queue()
MODEL_PATH = "vosk-model-small-en-us-0.15"
model = vosk.Model(MODEL_PATH)

active = False
silent = False
speaking = False
presentation_opened = False
launch_mode = False
presentation_auth_mode = False

last_command_time = 0
command_cooldown = 0.8
voice_block_time = 0.8
last_voice_time = 0

wake_words = ["siesta"]
launch_phrases = [
    "ignite deck",
    "command deck",
    "holo mode",
    "siesta prime",
    "open deck",
    "open presentation",
]

command_words = [
    "siesta",
    "ignite", "deck", "command", "holo", "mode", "prime", "open", "presentation",
    "verification", "code",
    "crimson", "access", "crison", "crimon", "krimson", "crimzon",
    "power", "on",
    "focus", "alpha", "wave", "echo", "rise", "trace", "yield", "clear",
    "a", "q", "w", "e", "r", "t", "y", "x",
    "screen",
    "one", "two", "three", "four", "five", "six", "seven",
    "zero", "1", "2", "3", "4", "5", "6", "7",
    "next", "previous", "back",
    "quiet", "continue", "shutdown", "sleep",
]

alias_to_key = {
    "focus": "a",
    "alpha": "q",
    "wave": "w",
    "echo": "e",
    "rise": "r",
    "trace": "t",
    "yield": "y",
    "clear": "x",
}

screen_alias_to_page = {
    "screen 1": "1",
    "screen 2": "2",
    "screen 3": "3",
    "screen 4": "4",
    "screen 5": "5",
    "screen 6": "6",
    "screen 7": "7",
    "screen one": "1",
    "screen two": "2",
    "screen three": "3",
    "screen four": "4",
    "screen five": "5",
    "screen six": "6",
    "screen seven": "7",
}

def word_to_number(text):
    numbers = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
    }
    for word, digit in numbers.items():
        text = text.replace(word, digit)
    return text

def normalize(text):
    fixes = {
        "ignit": "ignite",
        "dek": "deck",
        "holoo": "holo",
        "mod": "mode",
        "powar": "power",
        "pawar": "power",
        "nex": "next",
        "bak": "back",
        "previus": "previous",
        "scren": "screen",
        "screan": "screen",
        "skreen": "screen",
    }

    text = text.lower().strip()
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)

    text = word_to_number(text)
    text = " ".join(text.split())
    return text

def speak(text, force=False):
    global speaking

    if silent and not force:
        return

    def run():
        global speaking
        speaking = True
        window.set_mode("speaking")
        print("Siesta:", text)
        os.system(f'say -v Samantha -r 285 "{text}"')
        speaking = False
        window.set_mode("active" if active else "idle")

    threading.Thread(target=run, daemon=True).start()

def wake_word_detected(command):
    return any(fuzz.partial_ratio(word, command) > 85 for word in wake_words)

def launch_phrase_detected(command):
    return any(fuzz.partial_ratio(phrase, command) > 80 for phrase in launch_phrases)

def verification_detected(command):
    best_score = max(fuzz.partial_ratio(variant, command) for variant in PRESENTATION_PASSWORD_VARIANTS)
    print("Verification score:", best_score)
    return best_score >= 82

def open_presentation():
    global presentation_opened
    webbrowser.open(PRESENTATION_URL)
    presentation_opened = True
    time.sleep(2.5)
    speak("presentation ready", force=True)

def press_presentation_key(key_name):
    pyautogui.press(key_name)

def process_command(command):
    global active, launch_mode, presentation_auth_mode, silent
    global last_command_time, last_voice_time, presentation_opened

    if speaking:
        return

    if len(command) < 1:
        return

    if time.time() - last_voice_time < voice_block_time:
        return

    last_voice_time = time.time()
    command = normalize(command)
    print("You:", command)

    if time.time() - last_command_time < command_cooldown:
        return

    last_command_time = time.time()

    # Always allow wake again after shutdown
    if not active and wake_word_detected(command):
        active = True
        launch_mode = True
        window.set_mode("listening")
        speak("awaiting command", force=True)
        return

    if not active:
        return

    # Shutdown / sleep
    if "shutdown siesta" in command or "sleep siesta" in command:
        active = False
        launch_mode = False
        presentation_auth_mode = False
        presentation_opened = False
        window.set_mode("idle")
        speak("system offline", force=True)
        return

    # Mute / unmute
    if command == "quiet":
        silent = True
        return

    if command == "continue":
        silent = False
        speak("resuming", force=True)
        return

    # Launch flow
    if launch_phrase_detected(command):
        window.set_mode("active")
        speak("access granted, opening deck", force=True)
        threading.Thread(target=open_presentation, daemon=True).start()
        return

    # Presentation controls: NO speaking/repeating
    if presentation_opened:
        if command == "power on":
            press_presentation_key("enter")
            return

        if command in alias_to_key:
            press_presentation_key(alias_to_key[command])
            return

        if command in ["a", "q", "w", "e", "r", "t", "y", "x"]:
            press_presentation_key(command)
            return

        if command in screen_alias_to_page:
            press_presentation_key(screen_alias_to_page[command])
            return

        if command in ["1", "2", "3", "4", "5", "6", "7"]:
            press_presentation_key(command)
            return

        if command == "next":
            press_presentation_key("right")
            return

        if command in ["back", "previous"]:
            press_presentation_key("left")
            return

def audio_callback(indata, frames, time_info, status):
    if not speaking:
        audio_queue.put(bytes(indata))

def voice_loop():
    recognizer = vosk.KaldiRecognizer(model, 16000, json.dumps(command_words))

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                command = result.get("text", "")
                if command:
                    window.set_mode("listening")
                    process_command(command)
                    if not speaking:
                        window.set_mode("active" if active else "idle")

if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    app = QApplication(sys.argv)
    window = Sphere()
    window.show()
    threading.Thread(target=voice_loop, daemon=True).start()
    speak("Siesta ready. Say Siesta to activate.", force=True)
    sys.exit(app.exec())