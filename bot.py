from colorama import init
from termcolor import colored

from kb import KB


class Bot:
    """
    A class that represents the bot conducting the dialogue (SDS)
    """
    def __init__(self, name, speaker, listener):
        self.name = name
        self.speaker = speaker
        self.listener = listener
        self.kb = KB()
        self.color_bot = colored('Bot: ', 'red')
        self.color_user = colored('User: ', 'green')

        init(autoreset=True)
