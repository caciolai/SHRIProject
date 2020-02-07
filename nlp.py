import spacy

model_it = "it_core_news_sm"
model_en = "en_core_web_sm"

def syntax_analysis(sentence, language="it"):
    if language == "it":
        model = model_it
    elif language == "en":
        model = model_en
    else:
        raise NotImplementedError(f"Syntax analysis for {language} not implemented")

    nlp = spacy.load(model)
    doc = nlp(sentence)

    return doc


