import argparse
from spacy import displacy
from nltk import Tree
from texttable import Texttable


def build_argparser():
    """
    Builds a parser for command-line arguments
    :return: an argparser
    """
    parser = argparse.ArgumentParser(description='Waiter Bot')
    parser.add_argument('--dep_tree', action="store_true",
                        help='print dependencies tree of every heard sentence')

    return parser

def print_lemmas(sentence):
    t = Texttable()
    t.add_rows([["text", "lemma", "pos", "dep"]] +
               [[token.text, token.lemma_, token.pos_, token.dep_]
                 for token in sentence])

    print(t.draw())

def tok_format(tok):
    return f"{tok.text} ({tok.dep_})"

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)

def print_dependencies(sentence):
    to_nltk_tree(sentence.root).pretty_print()

def visualize_dependencies(doc):
    displacy.serve(doc, style="dep")