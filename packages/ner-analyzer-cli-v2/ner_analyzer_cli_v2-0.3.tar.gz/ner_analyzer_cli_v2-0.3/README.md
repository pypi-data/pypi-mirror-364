# ner_analyzer_cli_v2

A simple Named Entity Recognition (NER) analyzer package with a command-line interface (CLI) and export options for JSON and CSV. Powered by [spaCy](https://spacy.io/) and supporting multiple languages.

## Features

- Analyze text for named entities using spaCy.
- Supports multiple languages (`en`, `fr`, `de`, `es`, `pt`).
- Export results to JSON or CSV files.
- Shows entity frequency statistics.
- Easy-to-use CLI interface.

## Installation

First, install the package (after cloning or downloading):

```bash
pip install ner_analyzer_cli_v2
```

You must also download the relevant spaCy language model(s) as needed. For example:

```bash
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
# For other languages, see: https://spacy.io/models
```

## CLI Usage

```bash
ner-analyze "Your text to analyze here"
```

### Options

- `--output <file>`: Specify output file (`.json` or `.csv`).
- `--lang <code>`: Specify language code (`en`, `fr`, `de`, `es`, `pt`). Default is `en`.

#### Example

Analyze some text and export results:

```bash
ner-analyze "Barack Obama was born in Hawaii." --output results.json
ner-analyze "Emmanuel Macron est le président français." --lang fr --output results.csv
```

## Output Example

### Console

```
Entities:
[
  {
    "text": "Barack Obama",
    "label": "PERSON"
  },
  {
    "text": "Hawaii",
    "label": "GPE"
  }
]

Frequency:
{'PERSON': 1, 'GPE': 1}
```

### JSON

```json
{
  "entities": [
    {"text": "Barack Obama", "label": "PERSON"},
    {"text": "Hawaii", "label": "GPE"}
  ],
  "frequency": {"PERSON": 1, "GPE": 1}
}
```

### CSV

```
Entity,Label
Barack Obama,PERSON
Hawaii,GPE

Label,Count
PERSON,1
GPE,1
```

## API Usage

You can also use the `NERAnalyzer` class directly in your Python scripts:

```python
from ner_analyzer.cli import NERAnalyzer

analyzer = NERAnalyzer(lang_model="en_core_web_sm")
entities = analyzer.analyze_text("Angela Merkel was Chancellor of Germany.")
print(entities)
```

## License

MIT License

## Author

[Amal Alexander](https://www.linkedin.com/in/amal-alexander-305780131/)