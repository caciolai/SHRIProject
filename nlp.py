import spacy

model_it = "it_core_news_sm"
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


def find_compound(node, res):
    nodes = [child for child in node.children]
    while nodes:
        node = nodes.pop(0)
        if node.dep_ == "conj":
            res = f"{res} and {node.text}"
            return res
        elif node.dep_ == "compound" or node.dep_ == "amod":
            res = f"{node.text} {res}"
            return res

        for child in node.children:
            nodes.append(child)

    return res


def find_dep(parsed, dep):
    nodes = [parsed.root]
    while nodes:
        node = nodes.pop(0)
        if node.dep_ == dep:
            res = node.text
            return find_compound(node, res)

        for child in node.children:
            nodes.append(child)

    return None


def find_object(parsed):
    return find_dep(parsed, "dobj")


def find_subject(parsed):
    return find_dep(parsed, "nsubj")


def find_attribute(parsed):
    return find_dep(parsed, "attr")


def is_question(parsed):
    triggers = ["what", "how"]
    for t in triggers:
        if contains_lemma(parsed, t):
            return True

    return False
