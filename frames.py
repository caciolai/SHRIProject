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


class AskInfoFrame(Frame):
    # TODO: implement triggers
    def __init__(self):
        super().__init__()
        self.slots.update({
            "obj": None,
            "info": None
        })


class AddInfoFrame(Frame):
    # TODO: implement triggers
    def __init__(self):
        super().__init__()
        self.slots.update({
            "obj": None,
            "info": None
        })


entry_categories = [
    "starter",
    "main_course",
    "side_dish",
    "dessert",
    "drink"
]

order_categories = [
    "order"
]
class OrderFrame(Frame):
    @staticmethod
    def is_category(word):
        return word in entry_categories

    @staticmethod
    def is_trigger(word):
        return word in order_categories

    def __init__(self):
        super().__init__()
        self.slots.update({
            "starter": None,
            "main_course": None,
            "side_dish": None,
            "dessert": None,
            "drink": None
        })

end_triggers = [
    "bill",
    "enough"
]
class EndFrame(Frame):
    @staticmethod
    def is_trigger(word):
        return word in end_triggers

    def __init__(self):
        super().__init__()