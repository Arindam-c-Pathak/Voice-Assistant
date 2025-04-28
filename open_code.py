import customtkinter as ctk
import tkinter as tk
import geocoder
import nltk
import pyttsx3
from datetime import datetime
import os
import requests
import subprocess
from plyer import notification
import time
import threading
import random
from ytmusicapi import YTMusic
import webbrowser
import re
from googleapiclient.discovery import build
import speech_recognition as sr
from PIL import Image, ImageTk

#Speech settings for uniform set up
speech_engine = pyttsx3.init()
speech_engine.setProperty('rate', 180)
speech_engine.setProperty('volume', 1)
voices = speech_engine.getProperty('voices')
speech_engine.setProperty('voice', voices[1].id)

def music_player(song_name): #to play music
    yt = YTMusic()
    try:
        if not song_name:
            app.speak("Can you say that again?")
            return app.listener()
        elif song_name=="song" or song_name=="songs" or song_name=="some songs":
            app.speak("Playing your favourite song playlist.")
            webbrowser.open("Placeholder Url") #Replace this part with your personal playlist url
        else:
            search_results = yt.search(song_name)  # Search for a song
            if search_results:
                # Filter only songs from the results to avoid playlists or albums
                songs = [result for result in search_results if result['resultType'] == 'song']
                if songs:
                    top_result = songs[0]
                    video_id = top_result["videoId"]
                    title = top_result["title"]
                    artist = top_result["artists"][0]["name"]
                    app.speak(f"Playing {title} by {artist}.")
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    webbrowser.open(video_url)
                else:
                    app.speak("No song found in the search results.")
            else:
                app.speak("No results found.")
    except Exception as e:
        Entry = datetime.now().strftime("[%H:%M:%S] Error: ")
        app.Error_Log_File.write(f"{Entry}'{e}'\n")
        app.Error_Log_File.flush()

def get_weather(): #using weather api and geocoder to get the weather for the location of the IP
    weather_api_key = "Enter your API key here" #Replace with your own API key
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    city = geocoder.ip('me').city
    params = {
        'q': city,          
        'appid': weather_api_key, 
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        app.speak(f"Gathering the weather data for {city}")
        app.speak(f"Temperature is {temperature}°C\nand the Humidity is {humidity}% \nThe overall appearence of sky seems to be of {weather}")
    else:
        app.speak(f"Error: Unable to get weather data for {city}.")
        Entry = datetime.now().strftime("[%H:%M:%S] Error: ")
        e=f"Error: Unable to get weather data for {city}."
        app.Error_Log_File.write(f"{Entry}'{e}'\n")
        app.Error_Log_File.flush()

def running_programs(program_name): #Searches through the put together list of program paths and opens them
    app.speak("Looking through the files")
    prog_path={#Replace with your own program paths
        "app1": r"path:\to\the\app1.exe",
        "app2": r"path:\to\the\app2.exe"
        }
    path= prog_path.get(program_name.lower())
    if path and os.path.exists(path):
        try:
            app.speak(f"Opening {program_name}")
            subprocess.Popen([path])
        except Exception as e:
            Entry = datetime.now().strftime("[%H:%M:%S] Error: ")
            app.Error_Log_File.write(f"{Entry}'{e}'\n")
            app.Error_Log_File.flush()
            app.speak("Program not available in the list of programs. \nTry again.")
    else:
        e="Program not available"
        Entry = datetime.now().strftime("[%H:%M:%S] Error: ")
        app.Error_Log_File.write(f"{Entry}'{e}'\n")
        app.Error_Log_File.flush()
        app.speak("Program not available.")
        
def Searching(query): #Uses google custom search engine for searching stuff
    '''Searching Algorithm that opens link of top result'''
    api_key = "Api key here"
    cse_id = "CSE ID here"
    # Replace with your own API key and CSE ID
    service = build("customsearch", "v1", developerKey=api_key)
    results = service.cse().list(q=query, cx=cse_id, num=3).execute()
    app.speak("Here are the top results from Google")
    for item in results.get('items', []):
        app.speak(item['title'])
    app.speak("Opening top results in the browser")
    if 'items' in results and len(results['items']) > 0:
        i=0
        while i<len(results['items']):
            link = results['items'][i]['link']
            webbrowser.open(link)
            i=i+1

def set_timer(duration, reminder, message): #setting timers, just that
    app.speak(f"Timer set for {duration} seconds.")
    def countdown():        
        time.sleep(duration)
        send_notification(reminder, message)
        app.speak(message)
    # Create a thread to run the countdown in the background
    timer_thread = threading.Thread(target=countdown)
    timer_thread.start()

def send_notification(title, message): #sends notifications as needed
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Put the bot name here', 
            timeout=0
        )
    except Exception as e:
        Entry = datetime.now().strftime("[%H:%M:%S] Error: ")
        app.Error_Log_File.write(f"{Entry}'{e}'\n")
        app.Error_Log_File.flush()

def process_command(command): #for all the functions to be called using keywords
    words = nltk.word_tokenize(command.lower())
    if len(words)<=5: #keeping the input short just in case
        if "hello" in words or "hi" in words or "hey" in words or "heya" in words:
            # Greeting in response
            greet= [
                "Hello there.",
                "Hey.",
                "Sup?",
                "Hmm?",
                "Yeah?",
                "Wassup?"
                ]   
            i=random.randrange(0,len(greet))
            app.speak(greet[i])
    if "open" in words or "run" in words:
        # Opening programs
        if "open" in words:
            index = words.index("open")
            if index + 1 < len(words):
                program_name = words[index + 1]
        else:
            index = words.index("run")
            if index + 1 < len(words):
                program_name = words[index + 1]        
        running_programs(program_name)    
    if "timer" in words or "reminder" in words or "remind" in words:
        # Setting timers using math
        if "hour" in words or "hours" in words:
            timer1 = command.split("for", 1)[1].strip()
            timer = [int(s) for s in timer1.split() if s.isdigit()][0]
            duration = timer * 60 * 60
            set_timer(duration, 'Reminder', 'Time is up')        
        if "minute" in words or "minutes" in words:
            timer1 = command.split("for", 1)[1].strip()
            timer = [int(s) for s in timer1.split() if s.isdigit()][0]
            duration = timer * 60
            set_timer(duration, 'Reminder', 'Time is up')
        elif "second" in words or "seconds" in words:
            timer1 = command.split("for", 1)[1].strip()
            timer = [int(s) for s in timer1.split() if s.isdigit()][0]
            duration = timer
            set_timer(timer, 'Reminder', 'Time is up')        
        else:
            app.speak("Timer not set.")    
    if "play" in words or "music" in words or "song" in words or "songs" in words:
        # Playing songs
        if "play" in command: #only playing if it is specified
            song = command.split("play", 1)[1].strip()
            music_player(song)    
    if "weather" in words:
        # Checking weather
        get_weather()    
    if "search" in words or "find" in words:
        # Searching the web
        if "search" in words:
            query = command.split("search", 1)[1].strip()
        else:
            query = command.split("find", 1)[1].strip()
        Searching(query)    
    if "exit" in words or "bye" in words or "goodbye" in words or "shutdown" in words :
        # Closing program
        app.speak("Going offline")
        app.on_close()
    if "banish" in words:
        # Abort system by removing all procecess
        app.speak("Shutting down the apps and closing the system. See you later.")
        script= "shutdown /s /f /t 0"
        app.on_close()
        subprocess.run(script, shell=True)
    else:
        app.Chat_Log_File.write("\n")
        app.Chat_Log_File.flush()
        
# Initialize CustomTkinter for GUI
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")
class AssistantApp(ctk.CTk):  # GUI class for the front end
    def __init__(self):
        super().__init__()
        self.title("Bot name here") #replace with your own bot name
        self.geometry("120x100+0+0")
        self.configure(bg="#242424")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.canvas = tk.Canvas(self, width=80, height=80, bg="#242424", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.circle = self.canvas.create_oval(0, 0, 80, 80, fill="white")
        
        image = Image.open("path:\to\the\icon.png") #Replace with your own icon path
        image = image.resize((75, 75), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(image)

        # Add image to canvas (center coordinates should match the circle's center)
        self.image_item = self.canvas.create_image(40, 40, image=self.tk_image)

        self.shades = {
            "Idle": ["#b4b4b4", "#9b9b9b", "#a29b99", "#b3a8a5",],
            "Listening": ["#3A7BD5", "#3C7ED7", "#3F82D9", "#4185DB", "#4388DD", "#468BE0", "#488EE2", "#4A91E4", "#4D95E6", "#4F98E9"],
            "Speaking": ["#F9E79F", "#FAE88C", "#FBEB79", "#FCEC66", "#FDEE53", "#FEF040", "#FFF22D", "#FFF51A", "#FFF807", "#FFFF00"]
        }

        self.current_state = "Idle"
        self.color_index = 0
        self.animate_color()
    
        if not os.path.exists("Chat_Logs"):
            os.makedirs("Chat_Logs")
        if not os.path.exists("Error_Logs"):
            os.makedirs("Error_Logs")

        Daily_Date = datetime.now().strftime("%Y-%m-%d") #setting the date and opening the log files
        chat_log_file_path = f"Chat_Logs/Chat_log_{Daily_Date}.txt"
        self.Chat_Log_File = open(chat_log_file_path, "a", encoding="utf-8")
        self.Chat_Log_File.write("\n....New instance of the bot started....\n")
        error_log_file_path = f"Error_Logs/Error_log_{Daily_Date}.txt"
        self.Error_Log_File = open(error_log_file_path, "a", encoding="utf-8")
        self.Error_Log_File.write("\n....New instance of the bot started....\n")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        send_notification("Assistant name here", "System Online") #Replace with your own bot name
        self.running = False
        self.after(300, self.booting_sequence)
        self.start_listener_thread()

    def animate_color(self):
        if self.winfo_exists():
            try:
                shades = self.shades.get(self.current_state, ["white"])
                color = shades[self.color_index % len(shades)]
                self.canvas.itemconfig(self.circle, fill=color)
                self.color_index += 1
                self.after(33, self.animate_color)
            except tk.TclError:
                pass

    def on_close(self):
        self.Chat_Log_File.write("\n....Current instance ending....\n")
        self.Chat_Log_File.close()
        self.Error_Log_File.write("\n....Current instance ending....\n")
        self.Error_Log_File.close()
        self.destroy()

    def change_state(self, state):
        self.current_state = state
        self.color_index = 0  # Reset animation index for smooth loop

    def listener(self):
        while self.running:
            try:
                self.change_state("Listening")
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    try:
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=25)
                        text = recognizer.recognize_google(audio)
                        Entry = datetime.now().strftime("[%H:%M:%S] User: ")
                        self.Chat_Log_File.write(f"{Entry}'{text}'\n")
                        self.Chat_Log_File.flush()
                        self.triggers(text)
                    except sr.UnknownValueError:
                        self.change_state("Idle")
                        self.start_listener_thread()
                    except sr.WaitTimeoutError:
                        self.change_state("Idle")
                        self.start_listener_thread()
            except Exception as e:
                Entry = datetime.now().strftime("[%H:%M:%S] Error: ")
                self.Error_Log_File.write(f"{Entry}'{e}'\n")
                self.Error_Log_File.flush()

    def start_listener_thread(self):
        if not self.running:
            self.running = True
            listener_thread = threading.Thread(target=self.listener, daemon=True)
            listener_thread.start()

    def stop_listener_thread(self):
        self.running = False

    def speak(self, text):
        self.change_state("Speaking")
        Entry = datetime.now().strftime("[%H:%M:%S] Bot: ")
        self.Chat_Log_File.write(f"{Entry}'{text}'\n")
        self.Chat_Log_File.flush()
        speech_engine.say(text)
        speech_engine.runAndWait()
        self.change_state("Listening")

    def start_speak_thread(self, text):
        self.stop_listener_thread()
        threading.Thread(target=self.speak, args=(text,), daemon=True).start()
        self.start_listener_thread()

    def booting_sequence(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 8:
            self.speak("Early start for the day? Impressive.")
        elif 8 <= current_hour < 12:
            self.speak("Good Morning. Let's start the day.")
        elif 12 <= current_hour <= 16:
            self.speak("Good afternoon. Are we starting the day late?")
        elif 17 <= current_hour < 20:
            self.speak("Working in the evening? Let's start.")
        else:
            self.speak("It's a great night. Working overtime are we?")
        self.speak("What do you need?")

    def triggers(self, text):
        words = nltk.word_tokenize(text)
        commands = re.split(r'\band\b|\bthen\b|\balso\b', text.lower())
        for command in commands:
            command = command.strip()
            if command:
                process_command(command)

if __name__=="__main__":
    app = AssistantApp()
    app.mainloop()