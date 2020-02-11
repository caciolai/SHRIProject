import spacy

"""
File with all the NLP functions
"""


model_en = "en_core_web_sm"  # spacy model name for the english language


def syntax_analysis(sentence):
    """
    Performs syntax syntax analysis of the given sentence
    :param sentence: sentence
    :return: spacy dependency tree for the sentence
    """

    nlp = spacy.load(model_en)
    doc = nlp(sentence)
    parsed = list(doc.sents)[-1]
    return parsed

def contains_text(parsed, word):
    """
    Checks whether given parsed sentence contains given word
    :param parsed: parsed sentence
    :param word: word
    :return: bool
    """

    # explore dependency tree of the parsed sentence breadth-first, returing
    # if the word is found
    nodes = [parsed.root]
    while nodes:
        node = nodes.pop(0)
        if node.text == word:
            return True

        for child in node.children:
            nodes.append(child)

    return False

def find_dep(parsed, dep):
    """
    Searches a token with given dependency relation in the given dependency tree
    :param parsed: dependency tree of parsed sentence
    :param dep: dependency relation to look for
    :return: a tuple
                (token, descendant of token (None if leaf))
            if dep is present in parsed, None otherwise
    """

    # TODO: return all results instead of first one

    nodes = [parsed.root]
    while nodes:
        node = nodes.pop(0)
        if node.dep_ == dep:
            return (node, find_compound(node))

        for child in node.children:
            nodes.append(child)

    return None

def find_compound(node):
    """
    Completes the lemma in the given node by finding its compound term
    (descendant in the dependency tree)
    :param node: the node to complete
    :return: the compound term if present, None otherwise
    """

    allowed_dependency_relations = [
        "conj",         # conjunct (e.g. "fish and chips")
        "compound",     # compound (e.g. "french fries")
        "amod",         # adjectival modifier (e.g. "red meat")
        "advmod"        # adverbial modifier (e.g. "genetically modified")
    ]

    nodes = [child for child in node.children]
    while nodes:
        node = nodes.pop(0)

        if node.dep_ in allowed_dependency_relations:
            return node

        for child in node.children:
            nodes.append(child)

    return None

def reassemble_complex(tokens, lemma):
    """
    Reassebles a complex expression in the given token tuple found by find_dep
    according to their dependency relation
    :param tokens: token tuple (main token, child token [may be None])
    :param lemma: use the lemma_ of the tokens, otherwise use text
    :return: a tuple
                "{main token} and {child token}" or
                "{child token} {main token}"
    """

    if tokens is None:
        return None

    # if no child token, just return main token
    if tokens[1] is None:
        return tokens[0].lemma_ if lemma else tokens[0].text
    else:
        main, child = tokens
        str_main = main.lemma_ if lemma else main.text
        str_child = child.lemma_ if lemma else child.text
        if child.dep_ == "conj":
            # e.g. "fish and chips"
            return f"{str_main} and {str_child}"
        elif child.dep_ == "amod" or child.dep_ == "compound" or child.dep_ == "advmod":
            # e.g. "french fries"
            return f"{str_child} {str_main}"

def obtain_text(tokens):
    """
    Reassebles a complex expression in the given token tuple found by find_dep
    according to their dependency relation, using text of the tokens
    :param tokens: token tuple (main token, child token [may be None])
    :return: a tuple
                "{main token text} and {child token text}" or
                "{child token text} {main token text}"
    """

    return reassemble_complex(tokens, lemma=False)

def obtain_lemma(tokens):
    """
    Reassebles a complex expression in the given token tuple found by find_dep
    according to their dependency relation, using text of the tokens
    :param tokens: token tuple (main token, child token [may be None])
    :return: a tuple
                "{main token lemma} and {child token lemma}" or
                "{child token lemma} {main token lemma}"
    """

    return reassemble_complex(tokens, lemma=True)

def is_question(parsed):
    """
    Checks if parsed sentence is a question
    :param parsed: parsed sentence
    :return: bool
    """

    # simply checks if parsed sentence contains question triggers
    triggers = ["what", "how"]
    for t in triggers:
        if contains_text(parsed, t):
            return True

    return False
