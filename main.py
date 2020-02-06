import os, warnings
from colorama import init
from termcolor import colored

from listener import Listener
from nlp import syntax_analysis, print_lemmas, plot_dependency_graph
from speaker import Speaker
from utils import build_argparser

warnings.simplefilter("ignore")


LANG = "it"


if __name__ == '__main__':
    argparser = build_argparser()
    args = argparser.parse_args()

    l = Listener(language=LANG, mic_index=6)
    s = Speaker(language=LANG, rate=125, volume=1)
    # s = Speaker(language=LANG, rate=0, pitch=0, volume=0, spd=True)

    os.system("clear")

    sentence = l.listen()
    s.speak(sentence)

    doc = syntax_analysis(sentence, language=LANG)
    parsed = doc.sentences[0]
    plot_dependency_graph(parsed)
    print_lemmas(parsed)
    print(f"\n{'='*20}\n")
    doc.sentences[0].print_dependencies()
