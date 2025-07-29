
import spacy
import json

class NERAnalyzer:
    def __init__(self, model="en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            from spacy.cli import download
            download(model)
            self.nlp = spacy.load(model)

    def analyze_text(self, text):
        doc = self.nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        return entities

    def analyze_to_json(self, text):
        return json.dumps(self.analyze_text(text), indent=2)
