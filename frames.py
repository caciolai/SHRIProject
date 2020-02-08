class Frame:
    """
    A class that represents a generic frame
    """
    def __init__(self):
        self.slots = dict()

    def unfilled_slots(self):
        """
        :return: the slots left to fill
        """
        return [slot for slot, value in self.slots if value is None]

    def get_slot(self, slot):
        """
        :param slot: the slot
        :raises: AssertionError if slot is not in self.slots.keys()
        :return: value of the slot (None if not filled)
        """
        assert slot in self.slots

        return self.slots.get(slot)

    def fill_slot(self, slot, value):
        """
        :param slot: the slot
        :param value: the value for the slot
        :raises: AssertionError if slot is not in self.slots.keys() or
                                if slot is already filled
        :return: None
        """
        assert slot in self.slots
        assert self.slots[slot] is None

        self.slots[slot] = value

    def __str__(self):
        out = f"{self.__class__.__name__}: {self.slots}"
        return out

askinfo_triggers = {
    "ROOT": ["like", "ask"],
    "xcomp": ["see", "ask"],
    "advmod": ["how"],
    "amod": ["many"],
    "dobj": ["question", "calories"]
}
class AskInfoFrame(Frame):
    # TODO: implement triggers
    @staticmethod
    def is_trigger(word, dep):
        return dep in askinfo_triggers and word in askinfo_triggers[dep]

    def __init__(self):
        super().__init__()
        self.slots.update({
            "obj": None,
            "info": None
        })

addinfo_triggers = {
    "ROOT": ["add", "is"],
    "pobj": ["menu"],
}
class AddInfoFrame(Frame):
    # TODO: implement triggers
    @staticmethod
    def is_trigger(word, dep):
        return dep in addinfo_triggers and word in addinfo_triggers[dep]

    def __init__(self):
        super().__init__()
        self.slots.update({
            "subj": None,
            "obj": None,
            "info": None
        })


entry_courses = [
    "starter",
    "main course",
    "side dish",
    "dessert",
    "drink"
]

order_triggers = {
    "ROOT": ["like", "have"],
    "xcomp": ["order"],
    "pobj": ["course, dish, starter, drink, dessert"]
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
        self.slots.update({
            "starter": None,
            "main_course": None,
            "side_dish": None,
            "dessert": None,
            "drink": None
        })

end_triggers = {
    "ROOT": ["have"],
    "dobj": ["bill"]
}
class EndFrame(Frame):
    @staticmethod
    def is_trigger(word, dep):
        return dep in end_triggers and word in end_triggers[dep]

    def __init__(self):
        super().__init__()