import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import json
import webbrowser 
import datetime
import wikipedia
import os
import asyncio
import aiohttp
import base64
from random import randint
from PIL import Image
from io import BytesIO
import time
from typing import Optional, List
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 180)
        self.image_generator = ImageGenerator()
        self.df = None

    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def time_to_start(self):
        self.speak("Hello sir, I am your assistant. How can I help you?")

    def online_recognize(self):
        with sr.Microphone() as source:
            print("Listening (Online)...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                return None
        try:
            user_input = self.recognizer.recognize_google(audio)
            print("You said:", user_input)
            return user_input.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
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

    def handle_image_generation(self):
        self.speak("What would you like me to create? Please describe the image.")
        prompt = self.online_recognize() or self.offline_recognize()
        if not prompt:
            self.speak("I didn't get that. Please try again.")
            return
        self.speak(f"Generating images of {prompt}. This may take a moment...")
        try:
            image_paths = asyncio.run(self.image_generator.generate_images(prompt))
            if image_paths:
                self.image_generator.display_images(image_paths)
                self.speak(f"I've created {len(image_paths)} images for you. Check your screen.")
            else:
                self.speak("Sorry, I couldn't generate any images. Please try a different prompt.")
        except Exception as e:
            print(f"Error generating images: {e}")
            self.speak("There was an error generating the images. Let's try something else.")

    def handle_data_analysis(self):
        self.speak("Please select the CSV file for data analysis.")
        try:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select a CSV file",
                filetypes=[("CSV Files", "*.csv")]
            )
            if not file_path:
                self.speak("No file selected. Returning to main menu.")
                return
            self.df = pd.read_csv(file_path)
            summary = (
                f"The dataset has {self.df.shape[0]} rows and {self.df.shape[1]} columns. "
                f"Here are the column names: {', '.join(self.df.columns[:5])}."
            )
            self.speak(summary)
            print("\n🔍 DataFrame Info:")
            print(self.df.info())
            print("\n📊 Basic Statistics:")
            print(self.df.describe())
        except Exception as e:
            print(f"Error in data analysis: {e}")
            self.speak("There was an error processing the file.")

    def handle_graph_display(self):
        if self.df is None:
            self.speak("No dataset loaded yet. Please perform data analysis first.")
            return
        self.speak("Showing graph.")
        dept_avg_salary = self.df.groupby("Department")["Salary"].mean()
        dept_avg_salary.plot(kind="bar", title="Average Salary by Department")
        plt.ylabel("Average Salary")
        plt.tight_layout()
        plt.show()

        self.df["Age"].plot(kind="hist", bins=5, title="Age Distribution")
        plt.xlabel("Age")
        plt.tight_layout()
        plt.show()

    def handle_graph_change(self):
        if self.df is None:
            self.speak("No dataset loaded yet. Please perform data analysis first.")
            return
        self.speak("Changing the graph to different types.")

        plt.figure()
        plt.scatter(self.df["Age"], self.df["Salary"])
        plt.title("Scatter Plot: Age vs Salary")
        plt.xlabel("Age")
        plt.ylabel("Salary")
        plt.tight_layout()
        plt.show()

        plt.figure()
        self.df["Age"].plot(kind="hist", bins=5, title="Histogram of Age")
        plt.xlabel("Age")
        plt.tight_layout()
        plt.show()

        plt.figure()
        self.df.groupby("Department")["Salary"].mean().plot(kind="pie", autopct='%1.1f%%', title="Pie Chart: Avg Salary by Department")
        plt.ylabel("")
        plt.tight_layout()
        plt.show()

        plt.figure()
        self.df.boxplot(column="Salary", by="Department")
        plt.title("Box Plot: Salary by Department")
        plt.suptitle("")
        plt.ylabel("Salary")
        plt.tight_layout()
        plt.show()

    def handle_commands(self, user_input):
        if not user_input:
            return False
        if "hello" in user_input or "hi" in user_input:
            self.speak("Hello sir, how can I help you?")
        elif "bluetooth" in user_input:
            os.system("start ms-settings:bluetooth")
            self.speak("Opening Bluetooth settings, sir.")
        elif "date" in user_input:
            date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today's date is {date}")
        elif "time" in user_input:
            time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {time}")
        elif "open youtube" in user_input:
            webbrowser.open("https://www.youtube.com/")
            self.speak("Opening YouTube, sir")
        elif "summary" in user_input or "wikipedia" in user_input:
            self.handle_summary()
        elif "create an image" in user_input or "generate an image" in user_input or "draw" in user_input:
            self.handle_image_generation()
        elif "data analysis" in user_input:
            self.handle_data_analysis()
        elif "show me in the graph way" in user_input:
            self.handle_graph_display()
        elif "change the graph" in user_input:
            self.handle_graph_change()
        elif "stop" in user_input or "exit" in user_input or "sleep" in user_input:
            self.speak("Okay sir, I am going to sleep now.")
            return True
        return False

    def handle_summary(self):
        self.speak("What do you want me to search for?")
        while True:
            user_input = self.online_recognize() or self.offline_recognize()
            if not user_input:
                self.speak("I didn't catch that. Please try again.")
                continue
            if "back" in user_input or "cancel" in user_input:
                self.speak("Returning to main mode.")
                break
            try:
                result = wikipedia.summary(user_input, sentences=3)
                self.speak(f"According to Wikipedia: {result}")
                break
            except wikipedia.exceptions.DisambiguationError:
                self.speak("There are multiple options. Please be more specific.")
            except wikipedia.exceptions.PageError:
                self.speak("I couldn't find information on that topic. Try something else.")
            except Exception as e:
                print(f"Wikipedia error: {e}")
                self.speak("There was an error with Wikipedia. Let's try something else.")
                break

    def run(self):
        self.time_to_start()
        while True:
            user_input = self.online_recognize()
            if (not user_input) or (user_input and "offline" in user_input):
                user_input = self.offline_recognize()
            if self.handle_commands(user_input):
                break

class ImageGenerator:
    def __init__(self):
        self.api_url = "https://platform.stability.ai/account/keys"
        self.data_dir = os.path.join(os.path.expanduser("~"), "AssistantImages")
        os.makedirs(self.data_dir, exist_ok=True)
        self.timeout = aiohttp.ClientTimeout(total=60)

    async def generate_images(self, prompt: str, num_images: int = 4) -> List[str]:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            params = {"q": prompt}
            try:
                async with session.get(self.api_url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"API Error (Status {response.status}): {error_text}")
                        return []
                    data = await response.json()
                    images = data.get("images", [])[:num_images]
                    tasks = [self.download_image(session, img["src"], prompt, idx+1) for idx, img in enumerate(images)]
                    return await asyncio.gather(*tasks)
            except Exception as e:
                print(f"Error fetching images: {str(e)}")
                return []

    async def download_image(self, session: aiohttp.ClientSession, url: str, prompt: str, index: int) -> Optional[str]:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                image_data = await response.read()
                filename = f"{prompt.replace(' ', '_')[:50]}_{index}.jpg"
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                return filepath
        except Exception as e:
            print(f"Error downloading image {index}: {str(e)}")
            return None

    def display_images(self, image_paths: List[str]):
        for path in image_paths:
            if not path:
                continue
            try:
                img = Image.open(path)
                img.show()
                print(f"Displaying image: {os.path.basename(path)}")
            except Exception as e:
                print(f"Could not display image {path}: {str(e)}")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
