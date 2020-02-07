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
        if self._language == "it":
            self.say("Salve, come posso aiutarla?")
        elif self._language == "en":
            self.say("Hello, how may i help?")

    def say(self, sentence):
        print(f"{self._bot_prompt} {sentence}")
        self._speaker.speak(sentence)

    def listen(self):
        res = self._listen()
        while not res["success"]:
            err = res["error"]
            if isinstance(err, sr.UnknownValueError):
                if self._language == "it":
                    self.say("Scusi, non ho capito, potrebbe ripetere?")
                elif self._language == "en":
                    self.say("Sorry, I did not understand, can you say that again?")
            elif isinstance(err, sr.RequestError):
                if self._language == "it":
                    self.say("Impossibile comunicare con il server")
                elif self._language == "en":
                    self.say("No connection with the server available")
                    return None

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
        root = parsed.root.text.lower().strip()
        # print info if required
        if self._verbose:
            # self.say(f"La radice della frase è \'{root}\'")
            print(f"\n{'=' * 5} DEPENDENCIES OF SENTENCE {'=' * 5}")
            print_dependencies(parsed)
            print(f"\n{'=' * 5} TOKENS OF SENTENCE {'=' * 5}")
            print_lemmas(parsed)

        # if no previous interaction ongoing, create current frame
        # based on present parsed command
        if self._current_frame is None:
            frame = self._process(root, parsed)
            self._current_frame = frame

        # handle parsed command based on the current frame
        reply = None
        if isinstance(self._current_frame, EndFrame):
            self._goodbye()
            reply = None
        elif isinstance(self._current_frame, AddInfoFrame):
            reply = self._handle_add_info_frame(parsed)
        elif isinstance(self._current_frame, AskInfoFrame):
            reply = self._handle_ask_info_frame(parsed)
        elif isinstance(self._current_frame, OrderFrame):
            reply = self._handle_order_frame(parsed)

        return reply

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

    def _handle_add_info_frame(self, parsed):
        """
        Handles the slot filling of the current AddInfoFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        assert isinstance(self._current_frame, AddInfoFrame)

        # TODO: implement handling of AddInfoFrame

        return ""

    def _handle_ask_info_frame(self, parsed):
        """
        Handles the slot filling of the current AskInfoFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        assert isinstance(self._current_frame, AskInfoFrame)

        # TODO: implement handling of AskInfoFrame

        return ""

    def _handle_order_frame(self, parsed):
        """
        Handles the slot filling of the current OrderFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        assert isinstance(self._current_frame, OrderFrame)

        # TODO: implement handling of OrderFrame

        return ""

    def _goodbye(self):
        if self._language == "it":
            self.say("Ecco il conto. Arrivederci!")
        elif self._language == "en":
            self.say("Here's your bill. Goodbye!")

    def _ok(self):
        self.say("Ok.")

    def _load_kb(self, path):
        with open(f"./kb/{path}") as file:
            self._kb = json.load(file)

    def _save_kb(self):
        with open(f"./kb/{datetime.now().strftime('%Y%m%d-%H%M%S')}_kb.json", 'x') as f:
            json.dump(self._kb, f)
