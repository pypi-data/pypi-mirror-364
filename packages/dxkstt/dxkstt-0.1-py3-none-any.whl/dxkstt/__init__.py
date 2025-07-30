import speech_recognition as sr
import os
import threading
from mtranslate import translate
from colorama import Fore, Style, init
import pyaudio

init(autoreset=True)


def Translate_hindi_to_english(text):
    english_text = translate(text, 'en-us')
    return english_text


def print_loop():
    while True:
        print(Fore.LIGHTGREEN_EX + "I am Listening...", end='\r', flush=True)


def Speech_To_Text_Python():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 34000
    recognizer.dynamic_energy_adjustment_damping = 0.010
    recognizer.dynamic_energy_ratio = 1.0
    recognizer.pause_threshold = 0.3
    recognizer.operation_timeout = None
    recognizer.non_speaking_duration = 0.2

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            print(Fore.GREEN + "Listening...", end="", flush=True)
            try:
                audio = recognizer.listen(source, timeout=None)
                print("\r" + Fore.LIGHTBLACK_EX + "Recognizing...", end="", flush=True)
                recognizer_text = recognizer.recognize_google(audio).lower()

                if recognizer_text:
                    trans_text = Translate_hindi_to_english(recognizer_text)
                    print("\r" + Fore.BLUE + "Narayan: " + trans_text)
                else:
                    print(Fore.RED + "Didn't catch anything.")
            except sr.UnknownValueError:
                print(Fore.RED + "Could not understand audio.")
            except sr.RequestError as e:
                print(Fore.RED + f"API unavailable: {e}")
            finally:
                print("\r", end="", flush=True)


def main():
    stt_thread = threading.Thread(target=Speech_To_Text_Python)
    print_thread = threading.Thread(target=print_loop)

    stt_thread.start()
    print_thread.start()

    stt_thread.join()
    print_thread.join()


main()
