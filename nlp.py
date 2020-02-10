import spacy


model_en = "en_core_web_sm"

def syntax_analysis(sentence):
    """
    Returns syntax info about listened sentence
    :param sentence: listened sentence
    :return: a spacy token collection (sentence)
    """

    nlp = spacy.load(model_en)
    doc = nlp(sentence)
    parsed = list(doc.sents)[-1]
    return parsed


def contains_lemma(parsed, lemma):
    nodes = [parsed.root]
    while nodes:
        node = nodes.pop(0)
        if node.text == lemma:
            return True

        for child in node.children:
            nodes.append(child)

    return False


def find_compound(node):
    nodes = [child for child in node.children]
    while nodes:
        node = nodes.pop(0)
        if node.dep_ == "conj" or node.dep_ == "compound" or \
                node.dep_ == "amod" or node.dep_ == "advmod":
            return node

        for child in node.children:
            nodes.append(child)

    return None

def obtain_text(token_tuple):
    if token_tuple is None:
        return None

    if token_tuple[1] is None:
        return token_tuple[0].text
    else:
        if token_tuple[1].dep_ == "conj":
            return f"{token_tuple[0].text} and {token_tuple[1].text}"
        elif token_tuple[1].dep_ == "amod" or token_tuple[1].dep_ == "compound" \
                or token_tuple[1].dep_ == "advmod":
            return f"{token_tuple[1].text} {token_tuple[0].text}"

def obtain_lemma(token_tuple):
    if token_tuple is None:
        return None

    if token_tuple[1] is None:
        return token_tuple[0].lemma_
    else:
        if token_tuple[1].dep_ == "conj":
            return f"{token_tuple[0].lemma_} and {token_tuple[1].lemma_}"
        elif token_tuple[1].dep_ == "amod" or token_tuple[1].dep_ == "compound" \
                or token_tuple[1].dep_ == "advmod":
            return f"{token_tuple[1].lemma_} {token_tuple[0].lemma_}"

def find_dep(parsed, dep):
    nodes = [parsed.root]
    while nodes:
        node = nodes.pop(0)
        if node.dep_ == dep:
            return (node, find_compound(node))

        for child in node.children:
            nodes.append(child)

    return None

def is_question(parsed):
    triggers = ["what", "how"]
    for t in triggers:
        if contains_lemma(parsed, t):
            return True

    return False
