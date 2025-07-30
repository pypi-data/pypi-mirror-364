import re
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from functools import lru_cache
from sys import stdout, platform
from time import sleep
from subprocess import run
from os import system
from cryptography.fernet import Fernet
import requests
import threading
import pyttsx3
import speech_recognition as sr
import argparse as a
import json

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("punkt_tab", quiet=True)


class Bot:
    key = "p-tmqrG7yY09fgR5ck9yROUjfOMD3hT_SFS02K4dUkw="
    encrypted_url = "gAAAAABogu9gmgywMLw5WEV1PaXxNXlOKqb0E-_AyHsmeuwn1L5i124JlmmSUvInMm-A8PoUcYLJGVSXg99EeEI9seWRZRKChsAsZTNO1vohlG1H8BwvRDVqvAe-4RyueMQWxeWCViQ-hXBkGlEPaCOyfG73c05big=="
    key = key.encode()
    encrypted_url = encrypted_url.encode()
    cipher_suite = Fernet(key)
    url = cipher_suite.decrypt(encrypted_url).decode()

    def __init__(self, name):
        self.name = name
        self.conversations = []
        self.preprocessed_conversations = []
        self.conversations_loaded = threading.Event()
        self.is_load_custom_data = False
        self.file_path = None
        if not self.is_load_custom_data:
            threading.Thread(
                target=self.load_conversations_async,
                args=(self.url,),
            ).start()
        if self.is_load_custom_data:
            threading.Thread(
                target=self.load_custom_data,
                args=(self.file_path,),
            ).start()
        self.engine = pyttsx3.init()
        self.user_name = None
        self.is_speak = False
        import queue

        self.speak_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    @lru_cache(maxsize=None)
    def preprocess_text(self, text):
        corrected_text = str(TextBlob(text).correct())

        words = word_tokenize(corrected_text)

        clean_tokens = [re.sub(r"[^a-zA-Z0-9]", "", token).lower() for token in words]

        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()
        tokens = [
            lemmatizer.lemmatize(token)
            for token in clean_tokens
            if token not in stop_words
        ]

        tokens = [token for token in tokens if token]

        return tokens

    def speak(self, text):
        self.speak_queue.put(text)

    def _speech_worker(self):
        while True:
            text = self.speak_queue.get()
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error speaking text: {e}")
            self.speak_queue.task_done()

    def evaluate_math_expression(self, expr):
        try:
            math_match = re.fullmatch(r"[0-9+\-*/^(). ]+", expr)
            if math_match:
                result = eval(expr.replace("^", "**"))
                return f"The answer to '{expr.replace('**', '^')}' is {result}."
            else:
                return None
        except (SyntaxError, ValueError):
            return None
        except Exception as e:
            return f"Error: {e}"

    def generate_response(self, user_input):
        try:
            math_expression = self.evaluate_math_expression(user_input)
            if math_expression:
                return math_expression

            user_input_tokens = self.preprocess_text(user_input)
            if len(user_input) < 4:
                return f"Must be a minimum of 4 characters. Not {len(user_input)}."

            max_similarity = 0
            best_response = None

            for question_tokens, answers in self.preprocessed_conversations:
                if question_tokens and user_input_tokens:
                    common_tokens = set(question_tokens) & set(user_input_tokens)
                    similarity = len(common_tokens) / max(
                        len(question_tokens), len(user_input_tokens)
                    )
                else:
                    similarity = 0

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_response = random.choice(answers)

            if best_response:
                return best_response
            else:
                return "I'm sorry, I didn't understand your question."
        except Exception as e:
            return f"Error: {e}"

    def load_conversations_async(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.conversations = response.json()
            self.preprocessed_conversations = [
                (self.preprocess_text(entry["question"]), entry["answers"])
                for entry in self.conversations
            ]
            self.conversations_loaded.set()
        except Exception as e:
            typewriter(f"{self.name}: Error loading data: {e}")
            if self.is_speak:
                self.speak("Error loading data.")
            quit()

    def load_custom_data(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.conversations = json.load(file)
            self.preprocessed_conversations = [
                (self.preprocess_text(entry["question"]), entry["answers"])
                for entry in self.conversations
            ]
            self.conversations_loaded.set()
        except Exception as e:
            typewriter(f"{self.name}: Error loading custom data: {e}")
            if self.is_speak:
                self.speak("Error loading custom data.")
            quit()

    def listen_for_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            typewriter(f"{self.name}: Listening...\n")
            if self.is_speak:
                self.speak("Listening")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            typewriter(f"{self.name}: Recognizing...\n")
            if self.is_speak:
                self.speak("Recognizing")
            user_input = recognizer.recognize_google(audio)
            typewriter(f"You: {user_input}\n")
            if user_input.lower() == "exit":
                typewriter(f"{self.name}:Exiting speech mode...\n")
                return False
            response = self.generate_response(user_input)
            typewriter(f"{self.name}: {response}\n")
            if self.is_speak:
                self.speak(response)
        except sr.UnknownValueError:
            typewriter(f"{self.name}: Sorry, I could not understand your speech.")
            if self.is_speak:
                self.speak("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            typewriter(f"{self.name}: Speech recognition request failed: {e}")
            if self.is_speak:
                self.speak("Speech recognition request failed.")

    def set_user_name(self, new_name=None):
        if not new_name:
            new_name = input(f"{self.name}: What's your new name? ")
        self.user_name = new_name
        typewriter(f"{self.name}: Got it! I'll call you {self.user_name} from now on.")

    def get_user_name(self):
        if not hasattr(self, "user_name"):
            self.user_name = input(f"{self.name}: Hi! What's your name? ")
        return self.user_name


def typewriter(txt):
    for char in txt:
        stdout.write(char)
        stdout.flush()
        sleep(0.001)


def check_for_updates():
    current_version = "1.2.2"
    version_parts = list(map(int, current_version.split(".")))

    def version_to_str(parts):
        return ".".join(map(str, parts))

    def increment_version(parts):
        parts[2] += 1
        if parts[2] >= 100:
            parts[2] = 0
            parts[1] += 1
            if parts[1] >= 100:
                parts[1] = 0
                parts[0] += 1

    def decrement_version(parts):
        if parts[2] > 0:
            parts[2] -= 1
        elif parts[1] > 0:
            parts[1] -= 1
            parts[2] = 99
        else:
            parts[0] -= 1
            parts[1] = 99
            parts[2] = 99

    current_version_str = version_to_str(version_parts)
    while True:
        increment_version(version_parts)
        next_version_str = version_to_str(version_parts)
        response = requests.get(
            f"https://pypi.org/pypi/vsai/{next_version_str}/json"
        )
        if response.status_code == 404:
            decrement_version(version_parts)
            latest_version_str = version_to_str(version_parts)
            break

    latest_version = ".".join(map(str, version_parts))

    if latest_version > current_version:
        user_input = (
            input(
                f"New version {latest_version} available. Do you want to upgrade? (yes/no): "
            )
            .strip()
            .lower()
        )
        if user_input in ["yes", "y"]:
            if platform.lower().startswith("win"):
                run(["pip", "install", "vsai", "-U"])
            else:
                run(["pip3", "install", "vsai", "-U"])
        else:
            pass


def run():
    check_for_updates()
    parser = a.ArgumentParser(description="vsai Bot")
    parser.add_argument(
        "file", type=str, help="Path to the custom data file", nargs="?", default="None"
    )
    args = parser.parse_args()
    if args.file != "None":
        typewriter(f"Loading custom data from {args.file}...\n")
        bot = Bot(name="vsai")
        bot.is_load_custom_data = True
        bot.file_path = args.file
    else:
        bot = Bot(name="vsai")

    try:
        while True:
            if not bot.conversations_loaded.is_set():
                typewriter("Loading...")
                bot.conversations_loaded.wait()

                if platform.lower().startswith("win"):
                    system("cls")
                else:
                    system("clear")

            user_input = input("You: ")
            if user_input.lower() == "/speak on":
                bot.is_speak = True
                typewriter("Speech mode enabled.\n")
                if bot.is_speak:
                    bot.speak("Speech mode enabled.")
            elif user_input.lower() == "/speak off":
                bot.is_speak = False
                typewriter("Speech mode disabled.\n")
                if bot.is_speak:
                    bot.speak("Speech mode disabled.")
            elif user_input.lower() == "/name":
                bot.set_user_name()
            elif user_input.lower() == "/name?":
                typewriter(f"Your name is {bot.get_user_name()}.")
                if bot.is_speak:
                    bot.speak(f"Your name is {bot.get_user_name()}.")
            elif user_input.lower() == "/listen":
                while True:
                    bot.listen_for_input()
            elif user_input.lower() == "/exit":
                typewriter("Exiting...\n")
                break
            else:
                response = bot.generate_response(user_input)
                typewriter(f"{bot.name}: {response}\n")
                if bot.is_speak:
                    bot.speak(response)

    except KeyboardInterrupt:
        typewriter("\nExiting...\n")


if __name__ == "__main__":
    run()
