import warnings
from colorama import init
from termcolor import colored

from bot import Bot
from utils import *

warnings.simplefilter("ignore")


LANG = "it"


if __name__ == '__main__':
    init(autoreset=True)

    argparser = build_argparser()
    args = argparser.parse_args()

    # TODO: make it a command-line option
    bot = Bot("Bot", language=LANG, verbose=True)

    user_prompt = colored('User: ', 'green')
    while True:
        print(f"{user_prompt} ", end="")
        command = input()
        # command = bot.listen()
        print(f"{command}")

        reply = bot.process(command)

        if reply is None:
            break

