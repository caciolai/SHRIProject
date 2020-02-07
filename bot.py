import json
import datetime
import spacy
from colorama import init
from termcolor import colored

from speaker import Speaker
from listener import Listener, sr
from utils import *
from frames import *


model_it = "it_core_news_sm"
model_en = "en_core_web_sm"

class Bot:
    """
    A class that represents the bot conducting the dialogue (SDS)
    """
    END = "basta"
    COURSES = [
            "first_course",
            "second_course",
            "side_course",
            "dessert",
            "beverage",
    ]
    def __init__(self, name, language="it", verbose=True, kb_path=None):
        """
        Constructor
        :param name: the bot's name it will use in the dialogues
        :param language: the language (ISO code) of the conversation
        :param kb_path: the path of the stored kb
        """
        # TODO: implement KB for storing and retrieving information

        self._name = name
        self._language = language
        self._speaker = Speaker(language=language, rate=150, volume=1)
        self._listener = Listener(language=language, mic_index=0)
        self._bot_prompt = colored(f'{self._name}: ', 'red')
        self._verbose = verbose

        self._current_frame = None

        if kb_path is not None:
            self._load_kb(kb_path)
        else:
            self._kb = {"menu": []}

        init(autoreset=True)
        self.say("Salve, posso aiutarla?")

    def say(self, sentence):
        print(f"{self._bot_prompt} {sentence}")
        self._speaker.speak(sentence)

    def listen(self):
        res = self._listen()
        while not res["success"]:
            err = res["error"]
            if isinstance(err, sr.UnknownValueError):
                self.say("Scusi, non ho capito, potrebbe ripetere?")
            elif isinstance(err, sr.RequestError):
                self.say("Scusi, non sono in grado di capire, "
                         "questo ristorante non funziona senza una connessione internet "
                         "e al momento sembra non essercene una")
                break

            res = self._listen()

        return res["sentence"]

    def process(self, command):
        """
        Parses the command and recognizes the user intent thereby selecting
        the correct frame based upon the command root and then
        replying consistently
        :param command: command
        :return: a reply (None if interaction is over)
        """
        parsed = self._syntax_analysis(command)
        if self._current_frame is None:
            # no previous interaction ongoing
            root = parsed.root.text.lower().strip()
            if self._verbose:
                self.say(f"La radice della frase è \'{root}\'")
                print(f"\n{'=' * 5} DEPENDENCIES OF SENTENCE {'=' * 5}")
                print_dependencies(parsed)
                print(f"\n{'=' * 5} TOKENS OF SENTENCE {'=' * 5}")
                print_lemmas(parsed)

            frame = self._process(root, parsed)
            if isinstance(frame, EndFrame):
                self._goodbye()
                return None

            # TODO: handle other frames (first time)

        else:
            # TODO: handle ongoing frame
            pass

    def _process(self, root, parsed):
        # TODO: implement frame recognition
        if root == self.END:
            return EndFrame()

    def _listen(self):
        response = self._listener.listen()
        return response

    def _syntax_analysis(self, sentence):
        """
        Returns syntax info about listened sentence
        :param sentence: listened sentence
        :return: a spacy token collection (sentence)
        """
        if self._language == "it":
            model = model_it
        elif self._language == "en":
            model = model_en
        else:
            raise NotImplementedError(f"Syntax analysis for {self._language} not implemented")

        nlp = spacy.load(model)
        doc = nlp(sentence)
        parsed = list(doc.sents)[-1]
        return parsed

    def _add_menu_entry(self, name, course, calories=None, vegan=None):
        assert isinstance(name, str)
        assert self._kb.get(name, default=None) is None
        assert course in self.COURSES
        assert calories is None or calories > 0
        assert vegan is None or isinstance(vegan, bool)

        self._kb["entries"].append({"name":name,
                                    "course":course,
                                    "calories":calories,
                                    "vegan":vegan})

    def _update_menu_entry(self, name, course=None, calories=None, vegan=None):
        assert isinstance(name, str)
        assert self._kb.get(name, default=None) is not None
        assert course is None or course in self.COURSES
        assert calories is None or calories > 0

        for i, entry in enumerate(self._kb["entries"]):
            if entry["name"] == name:
                self._kb["entries"][i].update({"name":name,
                                    "course":course,
                                    "calories":calories,
                                    "vegan":vegan})

    def _get_menu_entry(self, name):
        assert isinstance(name, str)
        assert self._kb.get(name, default=None) is not None

        for i, entry in enumerate(self._kb["entries"]):
            if entry["name"] == name:
                return self._kb["entries"][i]

    def _goodbye(self):
        self.say("Arrivederci!")

    def _ok(self):
        self.say("Ok.")

    def _load_kb(self, path):
        with open(f"./kb/{path}") as file:
            self._kb = json.load(file)

    def _save_kb(self):
        with open(f"./kb/{datetime.now().strftime('%Y%m%d-%H%M%S')}_kb.json", 'x') as f:
            json.dump(self._kb, f)
