import stanfordnlp
from graphviz import Digraph
from texttable import Texttable

from utils import HiddenPrints


"""
File with all the NLP (syntax analysis) computation
"""

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
    g = Digraph('dependency_graph')

    with g.subgraph(name="cluster_0") as c:
        c.attr(color='blue')
        c.attr(label='words')
        for word in parsed_sentence.words:
            c.node(str(word.index), label=word.text)
            g.node(f"dep_{word.index}",
                   **{"label": str(word.dependency_relation),
                      "shape": "box",
                      "width": str(0.1), "height": str(0.05)})

            g.edge(f"dep_{word.index}", str(word.index))
            if word.governor != 0:
                g.edge(str(word.governor), f"dep_{word.index}")

    g.view()


def print_constituency_graph(sentence):
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
