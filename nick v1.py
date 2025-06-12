import speech_recognition as sr
import webbrowser 
import datetime
import pyttsx3 as pt
import wikipedia
import os
r = sr.Recognizer() 
global user

def time_to_start():
    pt.speak("Hello sir, I am your assistant. How can I help you?")
    print("Hello sir, I am your assistant. How can I help you?")
    # date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print(date)
    # pt.speak(f"The current time is {date}")

def recognizes():
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic, duration=0.1)
        print("Listening...")
        audio = r.listen(mic, phrase_time_limit=5)
        try:
            user = r.recognize_google(audio)
            print('You said: {}'.format(user))
            return user
        except sr.UnknownValueError:
            print("Sorry, I could not rr the audio. Please try again.")
            pt.speak("Sorry, I could not understand the audio. Please try again.")
            return None
        except sr.RequestError:
            print("the system is now offline sir , check your network connection ")
            pt.speak("the system is now offline sir , check your network connection.")
            return None

def summary(user):
    if user == "start summary":
        while True:
            pt.speak("What do you want me to search for you")
            print("What do you want me to search for you")
            user_input = recognizes()
            if user_input:
                if user_input == "come back":
                    print("ok sir, I am coming back to listening mode")
                    pt.speak("ok sir, I am coming back to listening mode")
                    break
                else:
                    result = wikipedia.summary(user_input, sentences=2)
                    print(result)
                    pt.speak(result)


def hello(user):
    if user == "hello":
        print("Hello sir, how can I help you?")
        pt.speak("Hello sir, how can I help you?")
def bluetooth(user):
    if user == "bluetooth":
        os.system("start ms:bluetooth")
        pt.speak("Opening Bluetooth settings, sir.")

def date(user):
    if user == "date":
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        print(date)
        pt.speak(f" the todays date is {date}")

def time(user):
    if user == "time":
        time = datetime.datetime.now().strftime("%H:%M")
        print(time)
        pt.speak(f" the current time is {time}")

def youtube(user):
        if user == "open YouTube":
            url = "https://www.youtube.com/"
            webbrowser.open(url)
            pt.speak("Opening Youtube sir ")
        
            
    

def stop(user):
    if user == "stop":
        print("ok sir i am sleeping now")
        pt.speak("ok sir, i am sleeping now")
        return True
    return False


if __name__ == '__main__':
    time_to_start()
    while True:
        user_input = recognizes()
        if user_input:
            summary(user=user_input)
            date(user=user_input)
            youtube(user=user_input)
            hello(user=user_input)
            time(user=user_input)
            bluetooth(user=user_input)
            
            
        
        if stop(user=user_input):
            break