from colorama import init
from termcolor import colored

from kb import KB


class Bot:
    """
    A class that represents the bot conducting the dialogue (SDS)
    """
    def __init__(self, name, speaker, listener):
        """
        Constructor
        :param name: the bot's name it will use in the dialogues
        :param speaker: the speaker object
        :param listener: the listener object
        """
        self.name = name
        self.speaker = speaker
        self.listener = listener
        self.kb = KB()
        self.color_bot = colored(f'{self.name}: ', 'red')
        self.color_user = colored('User: ', 'green')

        init(autoreset=True)

    def say(self, sentence):
        print(f"{self.color_bot} {sentence}")
        self.speaker.speak(sentence)