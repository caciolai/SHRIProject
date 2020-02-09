import json
from datetime import datetime
import os
from colorama import init
from termcolor import colored

from speaker import Speaker
from listener import Listener, sr
from utils import *
from frames import *
from exceptions import *
from nlp import *

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

        self._frame_stack = []
        self._current_frame = None

        self._is_over = False

        if menu_path is not None:
            self._load_menu(menu_path)
        else:
            self._menu = {"entries": []}

        init(autoreset=True)
        if self._language == "it":
            self._say("Salve, come posso aiutarla?")
        elif self._language == "en":
            self._say("Hello, how may i help?")

    def _say(self, sentence):
        print(f"{self._bot_prompt} {sentence}")
        self._speaker.speak(sentence)

    def listen(self):
        res = self._listen()
        while not res["success"]:
            err = res["error"]
            if isinstance(err, sr.UnknownValueError):
                if self._language == "it":
                    self._say("Scusi, non ho sentito, potrebbe ripetere?")
                elif self._language == "en":
                    self._say("Sorry, I did not hear that, can you say that again?")
            elif isinstance(err, sr.RequestError):
                if self._language == "it":
                    self._say("Impossibile comunicare con il server")
                elif self._language == "en":
                    self._say("No connection with the server available")
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

        parsed = syntax_analysis(command)

        if contains_lemma(parsed, "save"):
            self._save_menu()
            self._say("Menu saved")
            return
        if contains_lemma(parsed, "load"):
            self._load_menu()
            self._say("Menu loaded")
            return


        # print info if required
        if self._verbose:
            # root = parsed.root.text.lower().strip()
            # self.say(f"La radice della frase è \'{root}\'")
            print(f"\n{'=' * 5} DEPENDENCIES OF SENTENCE {'=' * 5}")
            print_dependencies(parsed)
            print(f"\n{'=' * 5} TOKENS OF SENTENCE {'=' * 5}")
            print_lemmas(parsed)

        frame = self._determine_frame(parsed)

        if self._current_frame is None:
            self._current_frame = frame
        elif type(frame) != type(self._current_frame):
            self._frame_stack.insert(0, self._current_frame)
            self._say("Ok we will come back to that later")
            self._current_frame = frame

        # handle parsed command based on the current frame
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
        else:
            # if current frame is still None, could not determine user intention
            reply = "I did not understand that, can you say that again?"

        self._say(reply)
        if self._current_frame is not None:
            self._current_frame.set_last_sentence(reply)

        print(self._current_frame)
        print(self._frame_stack)

        if self._current_frame is None and len(self._frame_stack) > 0:
            self._current_frame = self._frame_stack.pop(0)
            if isinstance(self._current_frame, AddInfoFrame):
                self._say("Ok now back to your statement")
            elif isinstance(self._current_frame, AskInfoFrame):
                self._say("Ok now back to your question")
            elif isinstance(self._current_frame, OrderFrame):
                self._say("Ok now back to your order")

            self._say(self._current_frame.get_last_sentence())

    def _determine_frame(self, parsed):
        if is_question(parsed):
            return AskInfoFrame()

        triggers_counts = self._count_frame_triggers(parsed)

        # could not determine frame
        if all([v == 0 for v in triggers_counts.values()]):
            return None

        frame_name = max(triggers_counts, key=triggers_counts.get)
        if frame_name == "EndFrame":
            return EndFrame()
        elif frame_name == "OrderFrame":
            return OrderFrame()
        elif frame_name == "AddInfoFrame":
            return AddInfoFrame()
        elif frame_name == "AskInfoFrame":
            return AskInfoFrame()

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
            if EndFrame.is_trigger(node.text, node.dep_):
                res["EndFrame"] += 1
            if OrderFrame.is_trigger(node.text, node.dep_):
                res["OrderFrame"] += 1
            if AddInfoFrame.is_trigger(node.text, node.dep_):
                res["AddInfoFrame"] += 1
            if AskInfoFrame.is_trigger(node.text, node.dep_):
                res["AskInfoFrame"] += 1

            for child in node.children:
                if not child in visited:
                    nodes.append(child)

        return res

    def _listen(self):
        response = self._listener.listen()
        return response

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
        Handles the current AddInfoFrame
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
                reply = "I am sorry, {} is not on the menu".format(entry)
            pass

        return reply

    def _fill_add_info_frame_slots(self, parsed):
        root = parsed.root.lemma_

        if root == "add":
            # add entry to menu
            entry = find_object(parsed)
            self._current_frame.fill_slot("subj", "menu")
            self._current_frame.fill_slot("obj", entry)
        elif root == "is":
            # add info about course
            entry = find_subject(parsed)
            course = find_attribute(parsed)
            self._current_frame.fill_slot("subj", "course")
            self._current_frame.fill_slot("obj", entry)
            self._current_frame.fill_slot("info", course)

    def _handle_ask_info_frame(self, parsed):
        """
        Handles the current AskInfoFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        assert isinstance(self._current_frame, AskInfoFrame)
        # TODO: fix asking menu (commas and spaces messed up)
        # TODO: check triggers ('i would like to know the desserts' does not work')
        reply = ""

        if len(self._menu["entries"]) == 0:
            reply = "I am sorry, there is nothing on menu today. Try and add something."
        else:
            obj = find_object(parsed)
            if obj == "menu":
                # if asked to see the menu
                # tell menu (entry, course) for each entry in menu
                reply = "We have "
                for course in entry_courses:
                    for entry in self._menu["entries"]:
                        if entry["course"] == course:
                            reply = f"{reply} {entry['name']}, "

                    reply += f"for {course}, "

                reply = reply[:-2]

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
        # TODO: allow to ask for recap
        assert isinstance(self._current_frame, OrderFrame)

        reply = ""
        old_frame_len = len(self._current_frame.filled_slots())
        try:
            self._fill_order_frame_slots(parsed)
        except EntryNotOnMenu:
            reply = "I am sorry, that is not on the menu"

        if len(self._current_frame.filled_slots()) == 0:
            # first interaction
            reply = "I am ready to take your order"
        else:
            if len(self._current_frame.unfilled_slots()) == 0 or \
                len(self._current_frame.filled_slots()) == old_frame_len:
                # user has made a full order or completed his order
                reply = "Ok. Your order is complete. It will come right away. Enjoy!"
                self._current_frame = None
            elif len(self._current_frame.filled_slots()) > old_frame_len:
                # user has added an entry to the order
                reply = "Ok. Do you want anything else?"

        return reply

    def _fill_order_frame_slots(self, parsed):
        root = parsed.root.lemma_
        xcomp = find_dep(parsed, "xcomp")
        dobj = find_dep(parsed, "dobj")

        if len(self._current_frame.filled_slots()) == 0 and \
                xcomp == "order" and dobj is None:
            # user is ready to order, but has not told anything yet
            return
        elif len(self._current_frame.filled_slots()) > 0 and root == "no":
            # user has completed his order
            return
        elif dobj is not None:
            # user has made an order for a menu entry
            entry = self._get_menu_entry(dobj)
            if entry is None:
                raise EntryNotOnMenu()

            self._current_frame.fill_slot(entry["course"], entry["name"])

    def _goodbye(self):
        self._is_over = True
        self._say("Here's your bill. Goodbye!")

    def is_over(self):
        return self._is_over

    def _ok(self):
        self._say("Ok.")

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
