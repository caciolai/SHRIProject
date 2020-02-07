import os, warnings

from bot import Bot
from listener import Listener
from nlp import *
from speaker import Speaker
from utils import build_argparser

warnings.simplefilter("ignore")


LANG = "it"


if __name__ == '__main__':
    argparser = build_argparser()
    args = argparser.parse_args()

    l = Listener(language=LANG, mic_index=0)
    s = Speaker(language=LANG, rate=125, volume=1)

    bot = Bot("Bot", listener=l, speaker=s)
    # sentence = l.listen()
    sentence = "La carbonara è un primo"
    bot.say(sentence)

    doc = syntax_analysis(sentence, language=LANG)
    parsed = doc.sentences[0]
    plot_dependency_graph(parsed)
    print_lemmas(parsed)
    print(f"\n{'='*20}\n")
    doc.sentences[0].print_dependencies()

    # parsed, dep_graph = core_syntax_analysis(sentence)
    #
    # print(parsed)
    # print(dep_graph)