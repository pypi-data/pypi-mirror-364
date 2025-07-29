import argparse
import json
import csv
import spacy
from ner_analyzer.utils import entity_frequency

class NERAnalyzer:
    def __init__(self, lang_model="en_core_web_sm"):
        self.nlp = spacy.load(lang_model)

    def analyze_text(self, text):
        doc = self.nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

def main():
    parser = argparse.ArgumentParser(description="Named Entity Recognition CLI Tool")
    parser.add_argument("text", type=str, help="Text to analyze")
    parser.add_argument("--output", type=str, help="File to save output (.json or .csv)")
    parser.add_argument("--lang", type=str, default="en", help="Language code (default: en)")

    args = parser.parse_args()

    # Map short lang code to spaCy model
    lang_models = {
        "en": "en_core_web_sm",
        "fr": "fr_core_news_sm",
        "de": "de_core_news_sm",
        "es": "es_core_news_sm",
        "pt": "pt_core_news_sm"
    }

    model_name = lang_models.get(args.lang, "en_core_web_sm")
    try:
        nlp = spacy.load(model_name)
    except OSError:
        print(f"Language model '{model_name}' not found. Run:\n  python -m spacy download {model_name}")
        return

    analyzer = NERAnalyzer(model_name)
    entities = analyzer.analyze_text(args.text)
    freq = entity_frequency(entities)

    print("Entities:")
    print(json.dumps(entities, indent=2))
    print("\nFrequency:")
    print(freq)

    if args.output:
        if args.output.endswith(".json"):
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump({"entities": entities, "frequency": freq}, f, indent=2, ensure_ascii=False)
            print(f"\nSaved to {args.output}")
        elif args.output.endswith(".csv"):
            with open(args.output, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Entity", "Label"])
                for e in entities:
                    writer.writerow([e["text"], e["label"]])
                writer.writerow([])
                writer.writerow(["Label", "Count"])
                for label, count in freq.items():
                    writer.writerow([label, count])
            print(f"\nSaved to {args.output}")
        else:
            print("Unsupported output format. Use .json or .csv")

if __name__ == "__main__":
    main()
