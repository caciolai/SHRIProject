from colorama import init
from termcolor import colored
from speaker import Speaker
from listener import Listener, sr

from kb import KB
from nlp import syntax_analysis, get_lemmas_info, find_root


INTERRUPT = "basta"

class Bot:
    """
    A class that represents the bot conducting the dialogue (SDS)
    """
    def __init__(self, name, language="it", verbose=True):
        """
        Constructor
        :param name: the bot's name it will use in the dialogues
        :param language: the language (ISO code) of the conversation
        """

        self.name = name
        self.language = language
        self.speaker = Speaker(language=language, rate=150, volume=1)
        self.listener = Listener(language=language, mic_index=0)
        self.kb = KB()
        self.bot_prompt = colored(f'{self.name}: ', 'red')
        self.verbose = verbose

        init(autoreset=True)
        self.say("Salve, posso aiutarvi?")

    def say(self, sentence):
        print(f"{self.bot_prompt} {sentence}")
        self.speaker.speak(sentence)

    def listen(self):
        res = self._listen()
        while not res["success"]:
            err = res["error"]
            if isinstance(err, sr.UnknownValueError):
                self.say("Scusi, non ho capito, potrebbe ripetere?")
            elif isinstance(err, sr.RequestError):
                self.say("Scusi, non sono in grado di capire, "
                         "questo ristorante non funziona senza una connessione internet "
                         "e al momento sembra non essercene una")
                break

            res = self._listen()

        return res["sentence"]

    def _listen(self):
        response = self.listener.listen()
        return response

    def _syntax_analysis(self, sentence):
        """
        Returns syntax info about listened sentence
        :param sentence: listened sentence
        :return: a tuple (dependency parse, lemmas info)
        """
        doc = syntax_analysis(sentence, self.language)
        parsed = doc.sentences[-1]
        lemmas_info = get_lemmas_info(parsed)
        return parsed, lemmas_info

    def process(self, sentence):
        parsed, lemmas_info = self._syntax_analysis(sentence)
        root = find_root(parsed).lower().strip()
        # plot_dependency_graph(parsed)
        if self.verbose:
            self.say(f"La radice della frase è {root}")
            print(f"\n{'=' * 5} DEPENDENCIES OF SENTENCE {'=' * 5}")
            parsed.print_dependencies()
            print(f"\n{'=' * 5} TOKENS OF SENTENCE {'=' * 5}")
            print(lemmas_info)

        if root == INTERRUPT:
            return True

    def goodbye(self):
        self.say("Arrivederci!")
