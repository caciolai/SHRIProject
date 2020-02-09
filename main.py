import warnings
from colorama import init
from termcolor import colored

from bot import Bot
from utils import *

warnings.simplefilter("ignore")


LANG = "en"


if __name__ == '__main__':
    init(autoreset=True)

    argparser = build_argparser()
    args = argparser.parse_args()

    bot = Bot("Bot", verbose=args.verbose)

    user_prompt = colored('User: ', 'green')
    while True:
        print(f"{user_prompt} ", end="")
        command = input()
        # command = bot.listen()
        # print(f"{command}")

        bot.process(command)

        if bot.is_over():
            break

