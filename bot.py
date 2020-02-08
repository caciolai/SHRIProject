import json
from datetime import datetime
import os
import spacy
from colorama import init
from termcolor import colored
import re

from speaker import Speaker
from listener import Listener, sr
from utils import *
from frames import *
from exceptions import *

model_it = "it_core_news_sm"
model_en = "en_core_web_sm"

class Bot:
    """
    A class that represents the bot conducting the dialogue (SDS)
    """
    def __init__(self, name, language="it", verbose=True, menu_path=None):
        """
        Constructor
        :param name: the bot's name it will use in the dialogues
        :param language: the language (ISO code) of the conversation
        :param menu_path: the path of the stored menu
        """

        self._name = name
        self._language = language
        self._speaker = Speaker(language=language, rate=150, volume=1)
        self._listener = Listener(language=language, mic_index=0)
        self._bot_prompt = colored(f'{self._name}: ', 'red')
        self._verbose = verbose

        self._current_frame = None

        if menu_path is not None:
            self._load_menu(menu_path)
        else:
            self._menu = {"entries": []}

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

        if command == "save menu":
            self._save_menu()
            return "Menu saved"
        elif command == "load menu":
            self._load_menu()
            return "Menu loaded"

        # TODO: instead of current frame, stack of frames
        parsed = self._syntax_analysis(command)
        # print info if required
        if self._verbose:
            # root = parsed.root.text.lower().strip()
            # self.say(f"La radice della frase è \'{root}\'")
            print(f"\n{'=' * 5} DEPENDENCIES OF SENTENCE {'=' * 5}")
            print_dependencies(parsed)
            print(f"\n{'=' * 5} TOKENS OF SENTENCE {'=' * 5}")
            print_lemmas(parsed)

        # if no previous interaction ongoing, create current frame
        # based on present parsed command
        if self._current_frame is None:
            frame = self._process(parsed)
            self._current_frame = frame
            # print(frame)

        # handle parsed command based on the current frame
        reply = None
        if isinstance(self._current_frame, EndFrame):
            self._goodbye()
            self._current_frame = None
            reply = None
        elif isinstance(self._current_frame, AddInfoFrame):
            reply = self._handle_add_info_frame(parsed)
        elif isinstance(self._current_frame, AskInfoFrame):
            reply = self._handle_ask_info_frame(parsed)
        elif isinstance(self._current_frame, OrderFrame):
            reply = self._handle_order_frame(parsed)

        # print(self._current_frame)
        # print(self._kb)

        return reply

    def _process(self, parsed):
        triggers_counts = self._count_frame_triggers(parsed)
        frame_name = max(triggers_counts, key=triggers_counts.get)
        if frame_name == "EndFrame":
            return EndFrame()
        elif frame_name == "OrderFrame":
            return OrderFrame()
        elif frame_name == "AddInfoFrame":
            return AddInfoFrame()
        elif frame_name == "AskInfoFrame":
            return AskInfoFrame()
        else:
            raise AssertionError

    def _count_frame_triggers(self, parsed):
        res = {
            "EndFrame": 0,
            "OrderFrame": 0,
            "AddInfoFrame": 0,
            "AskInfoFrame": 0
        }

        nodes = [parsed.root]
        visited = []
        while nodes:
            node = nodes.pop(0)
            visited.append(node)
            # print(node.text, node.dep_)
            if EndFrame.is_trigger(node.text, node.dep_):
                res["EndFrame"] += 1
            if OrderFrame.is_trigger(node.text, node.dep_):
                res["OrderFrame"] += 1
            if AddInfoFrame.is_trigger(node.text, node.dep_):
                res["AddInfoFrame"] += 1
            if AskInfoFrame.is_trigger(node.text, node.dep_):
                res["AskInfoFrame"] += 1

            # print(res)

            for child in node.children:
                if not child in visited:
                    nodes.append(child)

        return res

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

    def _find_compound(self, node, res):
        nodes = [child for child in node.children]
        while nodes:
            node = nodes.pop(0)
            if node.dep_ == "conj":
                res = f"{res} and {node.lemma_}"
                return res
            elif node.dep_ == "compound" or node.dep_ == "amod":
                res = f"{node.lemma_} {res}"
                return res

            for child in node.children:
                nodes.append(child)

        return res

    def _find_dep(self, parsed, dep):
        nodes = [parsed.root]
        while nodes:
            node = nodes.pop(0)
            if node.dep_ == dep:
                res = node.lemma_
                return self._find_compound(node, res)

            for child in node.children:
                nodes.append(child)

        return None

    def _find_object(self, parsed):
        return self._find_dep(parsed, "dobj")

    def _find_subject(self, parsed):
        return self._find_dep(parsed, "nsubj")

    def _find_attribute(self, parsed):
        return self._find_dep(parsed, "attr")

    def _add_menu_entry(self, name, course=None):
        if self._get_menu_entry(name) is not None:
            raise EntryAlreadyOnMenu()

        if course is not None and course not in entry_courses:
            raise CourseNotValid()

        self._menu["entries"].append({"name":name,
                                    "course":course})

    def _update_menu_entry(self, name, course=None):

        if course is not None and course not in entry_courses:
            raise CourseNotValid()

        entry = self._get_menu_entry(name)

        if entry is None:
            raise EntryNotOnMenu()

        if entry["course"] is not None:
            raise EntryAttributeAlreadySet()

        for i, entry in enumerate(self._menu["entries"]):
            if entry["name"] == name:
                self._menu["entries"][i].update({"name":name,
                                    "course":course})

    def _get_menu_entry(self, name):
        for i, entry in enumerate(self._menu["entries"]):
            if entry["name"] == name:
                return self._menu["entries"][i]

        return None

    def _handle_add_info_frame(self, parsed):
        """
        Handles the slot filling of the current AddInfoFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        assert isinstance(self._current_frame, AddInfoFrame)

        reply = ""
        self._fill_add_info_frame_slots(parsed)

        if self._current_frame.get_slot("subj") == "menu":
            # add entry to menu
            # TODO: prompt to add info about course
            try:
                self._add_menu_entry(self._current_frame.get_slot("obj"))
                reply = "Ok"
            except EntryAlreadyOnMenu:
                reply = "This entry is already in the menu"

            self._current_frame = None
        elif self._current_frame.get_slot("subj") == "course":
            # add info about course
            entry = self._current_frame.get_slot("obj")
            course = self._current_frame.get_slot("info")
            self._current_frame = None
            try:
                self._update_menu_entry(entry, course)
                reply = "Ok"
            except EntryAttributeAlreadySet:
                # TODO: add option to modify entry
                reply = "{} is already a {}".format(
                    entry,
                    self._get_menu_entry(entry)["course"]
                )
            except EntryNotOnMenu:
                # TODO: add option to add entry
                reply = "I am sorry, {} is not on the menu".format(
                    entry
                )
            pass

        return reply

    def _fill_add_info_frame_slots(self, parsed):
        root = parsed.root.text

        if root == "add":
            # add entry to menu
            entry = self._find_object(parsed)
            self._current_frame.fill_slot("subj", "menu")
            self._current_frame.fill_slot("obj", entry)
        elif root == "is":
            # add info about course
            entry = self._find_subject(parsed)
            course = self._find_attribute(parsed)
            self._current_frame.fill_slot("subj", "course")
            self._current_frame.fill_slot("obj", entry)
            self._current_frame.fill_slot("info", course)

    def _handle_ask_info_frame(self, parsed):
        """
        Handles the slot filling of the current AskInfoFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        assert isinstance(self._current_frame, AskInfoFrame)

        # TODO: implement handling of AskInfoFrame
        reply = ""
        obj = self._find_object(parsed)
        if obj == "menu":
            # if asked to see the menu
            # tell menu (entry, course) for each entry in menu
            reply = "We have " + \
                    ", ".join([entry["name"] for entry in self._menu["entries"]])

        elif obj in entry_courses:
            # if asked about a particular course
            # tell menu (entry, course) for each entry in menu if course == obj
            reply = "We have " + \
                    ", ".join([entry["name"] for entry in self._menu["entries"]
                               if entry["course"] == obj])

        self._current_frame = None
        return reply

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

    def _load_menu(self, path=None):
        if path is None:
            menus = os.listdir("./menu")
            menus.sort()
            path = menus[-1]
        with open(f"./menu/{path}") as file:
            self._menu = json.load(file)

    def _save_menu(self):
        with open(f"./menu/{datetime.now().strftime('%Y%m%d-%H%M%S')}_menu.json", 'x') as f:
            json.dump(self._menu, f)
