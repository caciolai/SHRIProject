import os
import stanfordnlp
from stanfordnlp.server import CoreNLPClient
from graphviz import Digraph
from texttable import Texttable

from utils import HiddenPrints


"""
File with all the NLP (syntax analysis) computation
"""

def core_semgrex(sentence, pattern):
    with CoreNLPClient(annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref'],
                       timeout=30000, memory='16G') as client:
        # Use semgrex patterns to directly find who wrote what.
        # pattern = '{word:wrote} >nsubj {}=subject >dobj {}=object'
        matches = client.semgrex(sentence, pattern)

        # sentences contains a list with matches for each sentence.
        # assert len(matches["sentences"]) == 3
        # length tells you whether or not there are any matches in this
        # assert matches["sentences"][1]["length"] == 1
        # You can access matches like most regex groups.
        # matches["sentences"][1]["0"]["text"] == "wrote"
        # matches["sentences"][1]["0"]["$subject"]["text"] == "Chris"
        # matches["sentences"][1]["0"]["$object"]["text"] == "sentence"

    return matches


config_en = {
	'processors': 'tokenize,mwt,pos,lemma,depparse', # Comma-separated list of processors to use
	'lang': 'en', # Language code for the language to build the Pipeline in
}

config_it = {
	'processors': 'tokenize,mwt,pos,lemma,depparse', # Comma-separated list of processors to use
	'lang': 'it', # Language code for the language to build the Pipeline in
}

def syntax_analysis(text, language="en"):
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

def print_lemmas(sentence):
    """
    Prints the information provided by NLP on the lemmas of a given sentence
    :param sentence: sentence
    :return: None
    """
    t = Texttable()
    t.add_rows([["text", "lemma", "upos", "xpos"]] +
                [[f'{word.text}', f'{word.lemma}', f'{word.upos}', f'{word.xpos}']
                 for word in sentence.words]
                )

    print(t.draw())

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


def plot_constituency_graph(sentence):
    g = Digraph('constituency_graph')

    idx = 0
    explored = []

    nodes = [(idx, sentence.parseTree.child[0])]
    g.node(str(idx), label=sentence.parseTree.child[0].value)

    while nodes:
        node_idx, node = nodes.pop(0)
        explored.append(node_idx)
        for child in node.child:
            idx += 1
            g.node(str(idx), label=child.value)
            g.edge(str(node_idx), str(idx))
            if str(child) not in explored:
                nodes.append((idx, child))

    g.view()

def core_syntax_analysis(sentence):

    # set up the client
    with CoreNLPClient(annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref'],
                       timeout=30000, memory='16G') as client:
        # submit the request to the server
        ann = client.annotate(sentence)

        # get the first sentence
        parsed = ann.sentence[0]

        # get the dependency parse of the first sentence
        dependency_parse = parsed.basicDependencies

        # # get the first token of the first sentence
        # token = parsed.token[0]
        #
        # # get the part-of-speech tag
        # print(token.pos)
        return parsed, dependency_parse
