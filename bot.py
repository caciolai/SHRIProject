import os, json
from datetime import datetime
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

    Attributes
    ----------
    _name: str
        the name of the bot
    _speaker: Speaker
        speaker object used for text to speech
    _listener: Listener
        listener object used for speech to perform Automatic Speech Recognition
    _prompt: str
        colored name of the bot to appear in the terminal
    _verbose: bool
        whether the bot should print info about the command it receives
        (dependency tree, lemmas info)
    _silent: bool
        whether the bot should only print replies (no text to speech)
    _frame_stack: list
        stack where the bot holds the frames it still has not finished to process
    _current_frame: Frame
        current frame the bot is processing
    _is_over: bool
        whether the interaction is over
    """
    def __init__(self, name, color, verbose=True, silent=False, menu_path=None):
        """
        Constructor
        :param name: the bot's name it will use in the dialogues
        :param color: the color the bot will use in the prompt
        :param verbose: whether the bot should print info about
        the command it receives (dependency tree, lemmas info)
        :param silent: if true, then only use print (no text to speech)
        :param menu_path: the path of the stored menu
        """

        self._name = name
        self._speaker = Speaker(rate=150, volume=1)
        self._listener = Listener(mic_index=0)
        self._prompt = colored(f'{self._name}: ', color)
        self._verbose = verbose
        self._silent = silent

        self._frame_stack = []
        self._current_frame = None

        self._is_over = False

        if menu_path is not None:
            self._load_menu(menu_path)
        else:
            self._menu = {"entries": []}

        # when finished setup, welcome user
        self._say(self._welcome())

    def _say(self, sentence):
        """
        Says the given sentence through the bot speaker object
        :param sentence: sentence
        :return: None
        """
        print(f"{self._prompt} {sentence}")
        if not self._silent:
            self._speaker.speak(sentence)

    def listen(self):
        """
        Tries to listen for commands.
        Loops until the sentence in understood properly or there is a connection error
        :return: transcribed sentence from voice
        """
        if self._verbose:
            print(f'{self._prompt} * listening *')
        res = self._listen()
        while not res["success"]:
            err = res["error"]
            if isinstance(err, sr.UnknownValueError):
                self._say("Sorry, I did not hear that, can you say that again?")
            elif isinstance(err, sr.RequestError):
                self._say("No connection with the server available")
                return None

            res = self._listen()

        return res["sentence"]

    def _listen(self):
        """
        A simple proxy to access bot own listener object and obtain
        the transcription of the voice command issued by the user
        :return: a response object (see Listener docs)
        """
        response = self._listener.listen()
        return response

    def process(self, command):
        """
        Processes the given command
        :param command: command
        :return: a proper reply (None if interaction is over)
        """

        # obtain spacy syntax dependency tree
        parsed = syntax_analysis(command)

        # if prompted to load last stored menu, or saved current one, do so
        if contains_text(parsed, "save"):
            self._save_menu()
            self._say("Menu saved")
            return
        if contains_text(parsed, "load"):
            self._load_menu()
            self._say("Menu loaded")
            return

        # print info if required
        if self._verbose:
            root = parsed.root.text.lower().strip()
            self._say(f"The root of the sentence is \'{root}\'")
            print(f"\n{'=' * 5} DEPENDENCIES OF SENTENCE {'=' * 5}")
            print_dependencies(parsed)
            print(f"\n{'=' * 5} TOKENS OF SENTENCE {'=' * 5}")
            print_tokens_info(parsed)

        # determine frame based on parsed command
        frame = self._determine_frame(parsed)

        # change current frame if necessary, storing old one
        if self._current_frame is None:
            self._current_frame = frame
        elif frame is not None and type(frame) != type(self._current_frame):
            self._frame_stack.insert(0, self._current_frame)
            # self._say("Ok we will come back to that later")
            self._current_frame = frame

        # obtain reply by handling parsed command based on the current frame
        if isinstance(self._current_frame, EndFrame):
            self._say(self._goodbye())
            self._current_frame = None
            self._frame_stack = []
            return
        elif isinstance(self._current_frame, AddInfoFrame):
            reply = self._handle_add_info_frame(parsed)
        elif isinstance(self._current_frame, AskInfoFrame):
            reply = self._handle_ask_info_frame(parsed)
        elif isinstance(self._current_frame, OrderFrame):
            reply = self._handle_order_frame(parsed)
        else:
            # if current frame is still None, could not determine user intention
            reply = "Sorry, I did not understand that, can you say that again?"

        self._say(reply)

        # if frame is not over yet, save current reply for later use
        if self._current_frame is not None:
            # self._current_frame.set_last_sentence(reply)
            self._set_last_sentence()

        # if older frame stored, restore it
        # and announce that bot is going back to older frame
        if self._current_frame is None and len(self._frame_stack) > 0:
            self._current_frame = self._frame_stack.pop(0)
            if isinstance(self._current_frame, AddInfoFrame):
                self._say("Ok now back to your statement")
            elif isinstance(self._current_frame, AskInfoFrame):
                self._say("Ok now back to your question")
            elif isinstance(self._current_frame, OrderFrame):
                self._say("Ok now back to your order")

            if self._current_frame.get_last_sentence() is not None:
                self._say(self._current_frame.get_last_sentence())

    def _determine_frame(self, parsed):
        """
        Determines the user intention based upon the parsed command and returns
        the appropriate frame to handle it
        :param parsed: parsed command (spacy tree)
        :return: appropriate frame
        """

        # if command is a question, then user is asking info
        if is_question(parsed):
            return AskInfoFrame()

        # otherwise, count the number of frame triggers for each frame
        triggers_counts = self._count_frame_triggers(parsed)

        # could not determine frame
        if all([v == 0 for v in triggers_counts.values()]):
            return None

        # return the frame with the majority of triggers
        # MIGHT NOT BE THE BEST METHOD
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
        """
        Counts the number of keywords for each frame triggered by the given
        parsed command
        :param parsed: parsed command
        :return: a dictionary {frame_name: triggers_count}
        """

        # setup return object
        res = {
            "EndFrame": 0,
            "OrderFrame": 0,
            "AddInfoFrame": 0,
            "AskInfoFrame": 0
        }

        # visit tree breadth-first, adding up the triggers along the way
        nodes = [parsed.root]
        visited = []
        while nodes:
            node = nodes.pop(0)
            visited.append(node)
            if EndFrame.is_trigger(node.lemma_, node.dep_):
                res["EndFrame"] += 1
            if OrderFrame.is_trigger(node.lemma_, node.dep_):
                res["OrderFrame"] += 1
            if AddInfoFrame.is_trigger(node.lemma_, node.dep_):
                res["AddInfoFrame"] += 1
            if AskInfoFrame.is_trigger(node.lemma_, node.dep_):
                res["AskInfoFrame"] += 1

            for child in node.children:
                if not child in visited:
                    nodes.append(child)

        return res

    def _add_menu_entry(self, name, course=None):
        """
        Adds an entry to the bot's menu to choose from
        :param name: name of the entry (e.g. hamburger)
        :param course: name of the course (optional, e.g. main course)
        :return: None
        """

        # consistency checks
        if self._get_menu_entry(name) is not None:
            raise EntryAlreadyOnMenu()

        if course is not None and course not in courses_names:
            raise CourseNotValid()

        self._menu["entries"].append({"name":name,
                                    "course":course})

    def _update_menu_entry(self, name, course=None):
        """
        Updates a menu entry (mainly adding info about course, but can be extended
        later on if needed)
        :param name: entry name
        :param course: course of the entry (e.g. drink)
        :return: None
        """

        # consistency checks
        if course is not None and course not in courses_names:
            raise CourseNotValid()

        entry = self._get_menu_entry(name)

        if entry is None:
            raise EntryNotOnMenu()

        if entry["course"] is not None:
            raise EntryAttributeAlreadySet()

        # update entry
        for i, entry in enumerate(self._menu["entries"]):
            if entry["name"] == name:
                self._menu["entries"][i].update({"name":name,
                                    "course":course})

    def _get_menu_entry(self, name):
        """
        Searches the given entry in the bot menu
        :param name: entry name
        :return: entry, None if absent
        """
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

        # consistency check
        assert isinstance(self._current_frame, AddInfoFrame)

        # fill current frame slots based on the parsed command
        reply = ""
        self._fill_add_info_frame_slots(parsed)

        # based on the frame slots, handle command
        if self._current_frame.get_slot("subj") == "menu":
            # add entry to menu
            try:
                entry = self._current_frame.get_slot("obj")
                self._add_menu_entry(entry)
                if self._current_frame.get_slot("info") is None:
                    reply = "Ok. What course is it?"
                    self._current_frame.set_waiting_answer(True)
                else:
                    course = self._current_frame.get_slot("info")
                    self._update_menu_entry(entry, course)
                    reply = "Ok"
                    self._current_frame = None
            except EntryAlreadyOnMenu:
                reply = "This entry is already in the menu"
                self._current_frame = None
        elif self._current_frame.get_slot("subj") == "course":
            # add info about course
            entry = self._current_frame.get_slot("obj")
            course = self._current_frame.get_slot("info")
            try:
                self._update_menu_entry(entry, course)
                reply = "Ok"
                self._current_frame = None
            except EntryAttributeAlreadySet:
                # TODO: add option to modify entry
                reply = "{} is already a {}".format(
                    entry,
                    self._get_menu_entry(entry)["course"]
                )
            except EntryNotOnMenu:
                # TODO: add option to add entry
                reply = "I am sorry, {} is not on the menu".format(entry)
            except CourseNotValid:
                reply = "I am sorry, {} is not a course".format(course)

        return reply

    def _fill_add_info_frame_slots(self, parsed):
        """
        Fills slots of the current AddInfoFrame based on the information
        contained in the given parsed command
        :param parsed: parsed command
        :return: None
        """
        root_lemma = parsed.root.lemma_
        pobj_lemma = obtain_lemma(find_dep(parsed, "pobj"))

        if root_lemma == "add" or pobj_lemma == "menu":
            # user wants to add entry to menu
            # TODO: allow to add entry and specify course at the same time
            self._current_frame.fill_slot("subj", "menu")
            entry = obtain_text(find_dep(parsed, "dobj"))
            self._current_frame.fill_slot("obj", entry)
            if pobj_lemma in courses_names:
                # user has also specified course
                self._current_frame.fill_slot("info", pobj_lemma)

        elif root_lemma == "is":
            # user wants to add info about course
            self._current_frame.fill_slot("subj", "course")
            entry = obtain_text(find_dep(parsed, "nsubj"))
            self._current_frame.fill_slot("obj", entry)
            course = obtain_lemma(find_dep(parsed, "attr"))
            self._current_frame.fill_slot("info", course)
        elif self._current_frame.is_waiting_answer():
            # user has responded to a previous question from the bot
            # (up to now, that might be only to add info about course of added entry)
            root_lemma = obtain_lemma(find_dep(parsed, "ROOT"))
            attr = obtain_lemma(find_dep(parsed, "attr"))
            course = root_lemma if root_lemma in courses_names else attr
            self._current_frame.fill_slot("subj", "course")
            self._current_frame.fill_slot("info", course)

    def _handle_ask_info_frame(self, parsed):
        """
        Handles the current AskInfoFrame
        :param parsed: the parsed command
        :return: consistent reply
        """
        # consistency check
        assert isinstance(self._current_frame, AskInfoFrame)

        # if nothing to ask about...
        if len(self._menu["entries"]) == 0:
            reply = "I am sorry, there is nothing on menu today. " \
                    "Try and add something or load the stored menu first."
            self._current_frame = None
            return reply

        # perform slot filling of current frame
        self._fill_ask_info_frame_slots(parsed)

        subj = self._current_frame.get_slot("subj")
        if subj == "menu":
            # if asked to see the menu
            # tell menu (entry, course) for each entry in menu
            reply = "We have:"
            for course in courses_names:
                if len([entry for entry in self._menu["entries"] if entry["course"] == course]) == 0:
                    continue

                for entry in self._menu["entries"]:
                    if entry["course"] == course:
                        reply = f"{reply} {entry['name']},"

                reply = reply[:-1]
                reply = f"{reply} for {course};"

            reply = reply[:-1]
        else:
            # if asked about a particular course
            # tell menu (entry, course) for each entry in menu if course == obj
            obj = self._current_frame.get_slot("obj")
            if obj in courses_names:
                reply = ""
                for entry in self._menu["entries"]:
                    if entry["course"] == obj:
                        reply = f"{reply} {entry['name']},"

                if len(reply) == "":
                    reply = f"I'm sorry, we don't have anything for {obj}"
                else:
                    reply = f"We have{reply[:-1]}"

            else:
                # the slot filling went wrong
                reply = "Sorry, I am not sure I understood your question"

        self._current_frame = None
        return reply

    def _fill_ask_info_frame_slots(self, parsed):
        """
        Fills slots of the current AskInfoFrame based on the information
        contained in the given parsed command
        :param parsed: parsed command
        :return: None
        """

        obj_lemma = obtain_lemma(find_dep(parsed, "dobj"))
        pobj_lemma = obtain_lemma(find_dep(parsed, "pobj"))

        if (obj_lemma is not None and obj_lemma == "menu") or \
                (pobj_lemma is not None and pobj_lemma == "menu"):
            # user has asked to know the menu
            self._current_frame.fill_slot("subj", "menu")
        else:
            # user has asked to know a course in particular
            self._current_frame.fill_slot("subj", "course")

            # to handle different possible phrasings of the question
            if obj_lemma is not None and obj_lemma in courses_names:
                self._current_frame.fill_slot("obj", obj_lemma)
            elif pobj_lemma is not None and pobj_lemma in courses_names:
                self._current_frame.fill_slot("obj", pobj_lemma)

    def _handle_order_frame(self, parsed):
        """
        Handles the current OrderFrame
        :param parsed: the parsed command
        :return: consistent reply
        """

        # consistency check
        assert isinstance(self._current_frame, OrderFrame)

        # if nothing to order...
        if len(self._menu["entries"]) == 0:
            reply = "I am sorry, there is nothing on menu today. " \
                    "Try and add something or load the stored menu first."
            self._current_frame = None
            return reply

        # try to perform slot filling
        try:
            self._fill_order_frame_slots(parsed)
        except EntryNotOnMenu:
            reply = "I am sorry, that is not on the menu"
            return reply

        # if first interaction and user did not specified anything
        if len(self._current_frame.filled_slots()) == 0:
            # if user asked for order recap
            if self._current_frame.get_asked_recap():
                reply = "You did not order anything yet, sir. " \
                        "I am ready to take your order"
            else:
                # user just said something like "i am ready to order"
                reply = "I am ready to take your order"
        else:
            # ongoing interaction
            if self._current_frame.get_asked_recap():
                reply = self._recap_order()
                self._current_frame.set_asked_recap(False)
                reply = f"{reply}. Would you like to add something else?"
                self._current_frame.set_waiting_confirmation(True)
            elif self._current_frame.is_waiting_confirmation() and \
                self._current_frame.get_user_answer() == "yes":
                # user said he wants something else
                reply = "Ok, please tell me"
                self._current_frame.set_waiting_confirmation(False)
            elif len(self._current_frame.unfilled_slots()) == 0 or \
                    (self._current_frame.is_waiting_confirmation() and
                    self._current_frame.get_user_answer() == "no"):
                # user has made a full order or said he does not want anything else
                reply = "Ok. Your order is complete. It will come right away. Enjoy!"
                self._current_frame.set_waiting_confirmation(False)
                self._current_frame = None
            else:
                # user has added an entry to the order
                reply = "Ok. Do you want anything else?"
                self._current_frame.set_waiting_confirmation(True)

        return reply

    def _fill_order_frame_slots(self, parsed):
        """
        Fills slots of the current OrderInfoFrame based on the information
        contained in the given parsed command
        :param parsed: parsed command
        :return: None
        """

        # get needed sentence parts to determine user intention
        root_lemma = parsed.root.lemma_
        xcomp_lemma = obtain_lemma(find_dep(parsed, "xcomp"))
        dobj_lemma = obtain_lemma(find_dep(parsed, "dobj"))
        dobj_text = obtain_text(find_dep(parsed, "dobj")) # need text for entry names
        advmod_lemma = obtain_lemma(find_dep(parsed, "advmod"))
        intj_lemma = obtain_lemma(find_dep(parsed, "intj"))
        det_lemma = obtain_lemma(find_dep(parsed, "det"))

        if self._current_frame.is_waiting_confirmation():
            # if bot is waiting for a binary answer ("do you want anything else?")
            if (root_lemma == "no" or intj_lemma == "no" or det_lemma == "no") \
                    and \
                (root_lemma != "have" and root_lemma != "like" and root_lemma != "take"):
                # user does not want anything else
                self._current_frame.set_user_answer("no")
                return
            elif (root_lemma == "yes" or intj_lemma == "yes") \
                    and \
                (not OrderFrame.is_trigger(root_lemma, "ROOT")):
                # user wishes to keep on with his order
                self._current_frame.set_user_answer("yes")
                return
            else:
                # user did not give a straight answer
                self._current_frame.set_user_answer(None)

        elif xcomp_lemma is None and dobj_lemma is None:
            # user said gibberish (as far as the bot knows...)
            # best thing is to just say 'that is not on the menu'
            raise EntryNotOnMenu

        if dobj_lemma == "order" and advmod_lemma == "so far":
            # user has asked to recap his order so far
            self._current_frame.set_asked_recap(True)
            return

        if len(self._current_frame.filled_slots()) == 0 and \
                xcomp_lemma == "order" and dobj_text is None:
            # user has just stated he is ready to order,
            # but has not ordered anything yet
            return

        if dobj_text is not None:
            # user has made an order for a menu entry,
            # add that to the current order if entry is on menu
            entry = self._get_menu_entry(dobj_text)
            if entry is None:
                raise EntryNotOnMenu()

            self._current_frame.fill_slot(entry["course"], entry["name"])

    def _recap_order(self):
        """
        Recaps the order made by the user so far
        :return: reply with the recap of the order
        """

        # consistency check
        assert isinstance(self._current_frame, OrderFrame)
        reply = "You ordered:"

        for course in courses_names:
            order_entry = self._current_frame.get_slot(course)
            if order_entry is not None:
                reply = f"{reply} {order_entry} for {course},"

        reply = f"{reply[:-1]}"

        return reply

    def _set_last_sentence(self):
        if isinstance(self._current_frame, AskInfoFrame):
            return
        elif isinstance(self._current_frame, AddInfoFrame):
            return
        elif isinstance(self._current_frame, EndFrame):
            return
        elif isinstance(self._current_frame, OrderFrame):
            if len(self._current_frame.filled_slots()) == 0:
                self._current_frame.set_last_sentence("I am ready to take your order")
            else:
                self._current_frame.set_last_sentence("Would you like anything else?")
                self._current_frame.set_waiting_confirmation(True)

    def _welcome(self):
        """
        Welcom message upon bot startup
        :return: welcome message
        """
        self._is_over = False
        return "Hello, how may I help?"

    def _goodbye(self):
        """
        Goodbye message upon bot termination
        :return: goodby message
        """
        self._is_over = True
        return "Here's your bill. Goodbye!"

    def is_over(self):
        return self._is_over

    def _load_menu(self, path=None):
        """
        Loads a menu
        :param path: menu path
        :return: None
        """
        if path is None:
            menus = os.listdir("./menu")
            menus.sort()
            path = menus[-1]
        with open(f"./menu/{path}") as file:
            self._menu = json.load(file)

    def _save_menu(self):
        """
        Saves the current menu on disk as a json file, at path timestamp_menu.json
        :return: None
        """
        with open(f"./menu/{datetime.now().strftime('%Y%m%d-%H%M%S')}_menu.json", 'x') as f:
            json.dump(self._menu, f)
