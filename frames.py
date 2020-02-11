class Frame:
    """
    A class that represents a generic frame
    """
    def __init__(self):
        self._slots = dict()
        self._last_sentence = None
        self._waiting_answer = False
        self._waiting_confirmation = False
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


entry_courses = [
    "starter",
    "main course",
    "side dish",
    "dessert",
    "drink"
]

askinfo_triggers = {
    "ROOT": ["like", "tell"],
    "xcomp": ["know"]
}
class AskInfoFrame(Frame):
    @staticmethod
    def is_trigger(word, dep):
        return dep in askinfo_triggers and word in askinfo_triggers[dep]

    def __init__(self):
        super().__init__()
        self._slots.update({
            "obj": None,        # menu, courses
        })

addinfo_triggers = {
    "ROOT": ["add", "is"]
}
class AddInfoFrame(Frame):
    @staticmethod
    def is_trigger(word, dep):
        return dep in addinfo_triggers and word in addinfo_triggers[dep]

    def __init__(self):
        super().__init__()
        self._slots.update({
            "subj": None,       # menu, course
            "obj": None,        # menu entry, menu entry
            "info": None        # None, course of the menu entry
        })



order_triggers = {
    "ROOT": ["like", "have"],
    "xcomp": ["order"],
    "dobj": ["order"],
    "advmod": ["so", "far"]
}
class OrderFrame(Frame):
    @staticmethod
    def is_category(word):
        return word in entry_courses

    @staticmethod
    def is_trigger(word, dep):
        return dep in order_triggers and word in order_triggers[dep]

    def __init__(self):
        super().__init__()
        self._slots.update({
            course: None for course in entry_courses
        })
        self._asked_recap = False

    def get_asked_recap(self):
        return self._asked_recap

    def set_asked_recap(self, v):
        self._asked_recap = v

end_triggers = {
    "dobj": ["bill"],
    "ROOT": ["shut"],
    "prt": ["down"]
}
class EndFrame(Frame):
    @staticmethod
    def is_trigger(word, dep):
        return dep in end_triggers and word in end_triggers[dep]

    def __init__(self):
        super().__init__()