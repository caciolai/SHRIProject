import argparse
from nltk import Tree
from texttable import Texttable


def build_argparser():
    """
    Builds a parser for command-line arguments
    :return: an argparser
    """
    parser = argparse.ArgumentParser(description='Waiter Bot')
    parser.add_argument('--verbose', action="store_true",
                        help='Print dependency tree and lemmas info '
                             'of every heard sentence')

    parser.add_argument('--keyboard', action="store_true",
                        help='Use keyboard instead of voice to interact with bot')

    return parser

def print_tokens_info(parsed):
    """
    Prints information about the tokens in the parsed sentence, in a tabular form:
    | word | lemma | POS tag | dependency relation in the sentence |
    :param parsed: parsed sentence
    :return: None
    """
    t = Texttable()
    t.add_rows([["word", "lemma", "pos", "dep"]] +
               [[token.text, token.lemma_, token.pos_, token.dep_]
                for token in parsed])

    print(t.draw())

"""
Functions to pretty print the dependency tree of a given parsed sentence
"""
def tok_format(tok):
    return f"{tok.text} ({tok.dep_})"

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
    else:
        return tok_format(node)

def print_dependencies(parsed):
    if len(list(parsed.root.children)) == 0:
        print(tok_format(parsed.root))
    else:
        to_nltk_tree(parsed.root).pretty_print()