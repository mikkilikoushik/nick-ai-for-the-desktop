import speech_recognition as sr
from ping3 import ping
from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import json
import webbrowser
import datetime
import wikipedia
import os
import time
import threading
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import subprocess

# =========================
# VOICE ASSISTANT CLASS
# =========================
class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 180)

        self.df = None
        self.hand_process = None  # HandMode()

        model_path = "vosk-model-en-us-0.42-gigaspeech"
        self.vosk_model = Model(model_path) if os.path.exists(model_path) else None

    def speak(self, text):
        print("Assistant:", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def time_to_start(self):
        self.speak("Hello sir. I am your assistant.")

    # =========================
    # SPEECH RECOGNITION
    # =========================
    def online_recognize(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, 1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            return self.recognizer.recognize_google(audio).lower()
        except:
            return None

    def offline_recognize(self):
        model_path = os.path.join(os.path.dirname(__file__), "vosk-model-en-us-0.22")
        if not os.path.exists(model_path):
            print("Vosk model not found! Falling back to online recognition.")
            return self.online_recognize()
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        stream.start_stream()
        print("Listening (Vosk, offline)...")
        start_time = time.time()
        while time.time() - start_time < 10:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_json = json.loads(result)
                user_input = result_json.get("text", "").lower()
                if user_input.strip():
                    print("You said:", user_input)
                    return user_input
        return None

    # =========================
    # OFFLINE MENU
    # =========================
    def offline_mode_menu(self):
        self.speak("System is offline. Press 1 for voice. Press 2 for help.")
        print("\n1) Voice\n2) Keyboard Help")
        return input("Choose (1/2): ").strip()

    def offline_keyboard_help(self):
        self.speak("Offline help mode activated.")
        print("""
Commands:
- hello
- time
- date
- data analysis
- show graph
- change graph
- start hand mode
- stop hand mode
- exit
Type 'back' to return
""")
        while True:
            cmd = input("Command: ").lower()
            if cmd == "back":
                return False
            if self.handle_commands(cmd):
                return True

    # =========================
    # DATA ANALYSIS
    # =========================
    def handle_data_analysis(self):
        self.speak("Please select the CSV file.")
        try:
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(
                title="Select CSV",
                filetypes=[("CSV Files", "*.csv")]
            )

            if not path:
                self.speak("No file selected.")
                return

            self.df = pd.read_csv(path)

            self.speak(
                f"Dataset loaded with {self.df.shape[0]} rows "
                f"and {self.df.shape[1]} columns."
            )

            print("\n🔍 Data Info:")
            print(self.df.info())
            print("\n📊 Statistics:")
            print(self.df.describe(include="all"))

        except Exception as e:
            print(e)
            self.speak("Error loading the dataset.")

    # =========================
    # GRAPH DISPLAY
    # =========================
    def handle_graph_display(self):
        if self.df is None:
            self.speak("No dataset loaded.")
            return

        num = self.df.select_dtypes(include="number").columns
        cat = self.df.select_dtypes(exclude="number").columns

        if len(num) == 0:
            self.speak("No numeric columns found.")
            return

        plt.figure()
        self.df[num[0]].plot(kind="hist", bins=5)
        plt.title(f"Histogram of {num[0]}")
        plt.tight_layout()
        plt.show()

        if len(cat) > 0:
            plt.figure()
            self.df.groupby(cat[0])[num[0]].mean().plot(kind="bar")
            plt.title(f"Average {num[0]} by {cat[0]}")
            plt.tight_layout()
            plt.show()

    # =========================
    # GRAPH CHANGE
    # =========================
    def handle_graph_change(self):
        if self.df is None:
            self.speak("No dataset loaded.")
            return

        num = self.df.select_dtypes(include="number").columns
        cat = self.df.select_dtypes(exclude="number").columns

        if len(num) < 2:
            self.speak("Not enough numeric columns.")
            return

        plt.figure()
        plt.scatter(self.df[num[0]], self.df[num[1]])
        plt.title(f"{num[0]} vs {num[1]}")
        plt.tight_layout()
        plt.show()

        if len(cat) > 0:
            plt.figure()
            self.df.groupby(cat[0])[num[1]].mean().plot(kind="pie", autopct="%1.1f%%")
            plt.title(f"{num[1]} by {cat[0]}")
            plt.tight_layout()
            plt.show()

    # =========================
    # COMMAND HANDLER
    # =========================
    def handle_commands(self, cmd):
        if not cmd:
            return False

        if "start hand mode" in cmd:
            self.speak("Hand mode activated.")
            self.hand_process = subprocess.Popen(["python", "ex.py"])

        elif "stop hand mode" in cmd:
            self.speak("Hand mode stopped.")
            self.hand_process.terminate()

        elif "data analysis" in cmd:
            self.handle_data_analysis()

        elif "show graph" in cmd:
            self.handle_graph_display()

        elif "change graph" in cmd:
            self.handle_graph_change()

        elif "time" in cmd:
            self.speak(datetime.datetime.now().strftime("%I:%M %p"))

        elif "date" in cmd:
            self.speak(datetime.datetime.now().strftime("%B %d, %Y"))

        elif "open youtube" in cmd:
            webbrowser.open("https://youtube.com")
            self.speak("Opening YouTube")

        elif "exit" in cmd or "stop" in cmd:
            self.speak("Goodbye.")
            self.hand_mode.stop()
            return True

        return False


# =========================
# NETWORK CHECK
# =========================
def network_check():
    try:
        return ping("8.8.8.8", timeout=2) is not None
    except:
        return False


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.time_to_start()

    while True:
        if network_check():
            text = assistant.online_recognize()
            if assistant.handle_commands(text):
                break
        else:
            choice = assistant.offline_mode_menu()
            if choice == "1":
                text = assistant.offline_recognize()
                if assistant.handle_commands(text):
                    break
            elif choice == "2":
                if assistant.offline_keyboard_help():
                    break