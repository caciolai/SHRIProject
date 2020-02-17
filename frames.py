class Frame:
    """
    A class that represents a generic frame, extended by specific frames
    with slots suited for the specific interaction

    Attributes
    ----------
    _slots: dict
        a dictionary with the slots {slot: slot value}
    _last_sentence: str
        last sentence pronounced by the bot in the frame
    _waiting_confirmation: bool
        whether bot is waiting for a dicotomic answer in the frame
    _waiting_answer: bool
        whether bot is waiting for a generic answer (not yes/no) in the frame
    _user_answer: str
        the answer of the user to the previous question from the bot
    """
    def __init__(self):
        self._slots = dict()
        self._last_sentence = None
        self._waiting_confirmation = False
        self._waiting_answer = False
        self._user_answer = None

    def filled_slots(self):
        """
        :return: the slots filled so far
        """
        return [slot for slot, value in self._slots.items() if value is not None]

    def unfilled_slots(self):
        """
        :return: the slots left to fill
        """
        return [slot for slot, value in self._slots.items() if value is None]

    def get_slot(self, slot):
        """
        :param slot: the slot
        :raises: AssertionError if slot is not in self.slots.keys()
        :return: value of the slot (None if not filled)
        """
        assert slot in self._slots

        return self._slots.get(slot)

    def fill_slot(self, slot, value):
        """
        :param slot: the slot
        :param value: the value for the slot
        :raises: AssertionError if slot is not in self.slots.keys() or
                                if slot is already filled
        :return: None
        """
        assert slot in self._slots

        self._slots[slot] = value

    def set_last_sentence(self, sentence):
        self._last_sentence = sentence

    def get_last_sentence(self):
        return self._last_sentence

    def set_waiting_confirmation(self, v):
        self._waiting_confirmation = v

    def is_waiting_confirmation(self):
        return self._waiting_confirmation

    def set_waiting_answer(self, v):
        self._waiting_answer = v

    def is_waiting_answer(self):
        return self._waiting_answer

    def get_user_answer(self):
        return self._user_answer

    def set_user_answer(self, v):
        self._user_answer = v

    def __str__(self):
        out = f"{self.__class__.__name__}: {self._slots}"
        return out


# courses supported
courses_names = [
    "starter",
    "main course",
    "side dish",
    "dessert",
    "drink"
]


class AskInfoFrame(Frame):
    """
    Frame that represents the intention of asking information.
    Slots to be filled are:
        subj: the subject of the information required (menu entries, course entries)
        obj: the object to ask information about
    """
    @staticmethod
    def is_trigger(token, dep):
        """
        Checks if the given token with the given dependency relation
        is a trigger for the frame
        :param token: token (word or lemma)
        :param dep: dependency relation
        :return: bool
        """
        askinfo_triggers = {
            "ROOT": ["like", "tell"],
            "xcomp": ["know"]
        }
        return dep in askinfo_triggers and token in askinfo_triggers[dep]

    def __init__(self):
        super().__init__()
        self._slots.update({
            "subj": None,        # menu, courses
            "obj": None,         # None, specific course
        })


class AddInfoFrame(Frame):
    """
    Frame that represents the intention of adding information.
    Slots to be filled are:
        subj: the subject of the information added (menu entries, course of an entry)
        obj: entry name
        info: course of the entry
    """
    @staticmethod
    def is_trigger(token, dep):
        """
        Checks if the given token with the given dependency relation
        is a trigger for the frame
        :param token: token (word or lemma)
        :param dep: dependency relation
        :return: bool
        """
        addinfo_triggers = {
            "ROOT": ["add", "is", "like", "want"],
            "xcomp": ["add"]
        }
        return dep in addinfo_triggers and token in addinfo_triggers[dep]

    def __init__(self):
        super().__init__()
        self._slots.update({
            "subj": None,       # menu, course
            "obj": None,        # menu entry, menu entry
            "info": None        # None, course of the menu entry
        })


class OrderFrame(Frame):
    """
    Frame that represents the intention of ordering food.
    Slots to be filled are:
        course: the entry for the course
    for each course (starter, main course, side dish, dessert, drink)
    """
    @staticmethod
    def is_trigger(token, dep):
        """
        Checks if the given token with the given dependency relation
        is a trigger for the frame
        :param token: token (word or lemma)
        :param dep: dependency relation
        :return: bool
        """
        order_triggers = {
            "ROOT": ["like", "have"],
            "xcomp": ["order"],
            "dobj": ["order"],
            "advmod": ["so", "far"]
        }
        return dep in order_triggers and token in order_triggers[dep]

    def __init__(self):
        super().__init__()
        self._slots.update({
            course: None for course in courses_names  # course: entry for course
        })
        self._asked_recap = False

    def get_asked_recap(self):
        return self._asked_recap

    def set_asked_recap(self, v):
        self._asked_recap = v


class EndFrame(Frame):
    """
    Frame that represents the intention of ending the interaction.
    """
    @staticmethod
    def is_trigger(token, dep):
        """
        Checks if the given token with the given dependency relation
        is a trigger for the frame
        :param token: token (word or lemma)
        :param dep: dependency relation
        :return: bool
        """
        end_triggers = {
            "dobj": ["bill"],
            "ROOT": ["shut", "goodbye"],
            "prt": ["down"]
        }
        return dep in end_triggers and token in end_triggers[dep]

    def __init__(self):
        super().__init__()