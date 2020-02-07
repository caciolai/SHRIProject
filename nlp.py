import os
import stanfordnlp
from graphviz import Digraph

from utils import HiddenPrints


config_en = {
	'processors': 'tokenize,mwt,pos,lemma,depparse', # Comma-separated list of processors to use
	'lang': 'en', # Language code for the language to build the Pipeline in
}

config_it = {
	'processors': 'tokenize,mwt,pos,lemma,depparse', # Comma-separated list of processors to use
	'lang': 'it', # Language code for the language to build the Pipeline in
}

def syntax_analysis(text, language):
    """
    Given some text, perform syntax analysis
    :param text: the text to analyse
    :param language: the language of the text
    :return: the doc object containing sentences with words, each with
                - lemma
                - upos
                - xpos
                - depend_relation and its governor
    """
    if language == "it":
        config = config_it
    elif language == "en":
        config = config_en
    else:
        raise AssertionError("No language with code \'{}\' supported".format(language))

    with HiddenPrints():
        nlp = stanfordnlp.Pipeline(**config)    # Initialize the pipeline using a configuration dict
        doc = nlp(text)                         # Run the pipeline on input text

    return doc

def get_lemmas_info(parsed_sentence):
    """
    Get the information provided by NLP on the lemmas of a given sentence
    :param parsed_sentence: sentence from nlp(...)
    :return: None
    """
    lemmas_info = [{
        "text": word.text,
        "lemma": word.lemma,
        "upos": word.upos,
        "xpos": word.xpos
    } for word in parsed_sentence.words]

    return lemmas_info

def find_root(parsed_sentence):
    for word in parsed_sentence.words:
        if word.governor == 0:
            return word.text

def print_lemmas(parsed_sentence):
    """
    Prints the information provided by NLP on the lemmas of a given sentence
    :param parsed_sentence: sentence
    :return: None
    """
    print(*[f'text: {word.text + " "}\tlemma: {word.lemma}\tupos: {word.upos}\txpos: {word.xpos}'
            for word in parsed_sentence.words], sep='\n')

def plot_dependency_graph(parsed_sentence):
    """
    Plots the dependency graph of a parsed sentence
    :param parsed_sentence: the collection of words with their NLP info
    :return: None
    """

    if not "graphviz" in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + 'C:/Users/Andrea/graphviz-2.38/bin'

    g = Digraph('dependency_graph')

    with g.subgraph(name="cluster_0") as c:
        for word in parsed_sentence.words:
            c.node(str(word.index), label=word.text)
            g.edge(f"dep_{word.index}", str(word.index))
            if word.governor != 0:
                g.edge(str(word.governor), f"dep_{word.index}")

    with g.subgraph(name="cluster_1") as c:
        for word in parsed_sentence.words:
            c.node(f"dep_{word.index}",
                   **{"label": str(word.dependency_relation),
                      "shape": "box",
                      "width": str(0.1), "height": str(0.05)})

    g.view()

