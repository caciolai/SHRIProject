import warnings
from colorama import init
from termcolor import colored

from bot import Bot
from utils import *


BOT_COLOR = 'red'
USER_COLOR = 'green'


if __name__ == '__main__':

    # ignore warnings
    warnings.simplefilter("ignore")

    # initialize colorama
    init(autoreset=True)

    # parse command-line arguments
    argparser = build_argparser()
    args = argparser.parse_args()

    # initialize bot
    bot = Bot("Bot", color=BOT_COLOR, verbose=args.verbose)

    # setup colored prompt for user
    user_prompt = colored('User: ', USER_COLOR)

    # while interaction is not over
    while not bot.is_over():
        # obtain command (ASR or keyboard)
        if args.keyboard:
            print(f"{user_prompt} ", end="")
            command = input()
        else:
            command = bot.listen()
            if command is None:
                break
            print(f"{user_prompt} {command}")

        # process command (bot will reply accordingly)
        bot.process(command)
