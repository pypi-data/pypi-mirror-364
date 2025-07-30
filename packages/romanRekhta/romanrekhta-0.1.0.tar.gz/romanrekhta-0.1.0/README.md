# 🇵🇰 romanRekhta

**romanRekhta** is a lightweight, flexible, and extensible Python library for **Roman Urdu Natural Language Processing (NLP)**. It provides essential tools for text preprocessing, tokenization, and stopword removal tailored to Roman Urdu, a widely used informal script across Pakistan and South Asia.

---

## Features

- Modular preprocessing (lowercasing, punctuation removal, emoji handling)
- Flexible stopword filtering (from `.txt` file or custom list)
- Tokenization (word and sentence level)
- Easily extendable and community-contributable

---

## Installation

```bash
pip install -e .
# When published
pip install romanRekhta
```

---

## Quick Start

```python
from romanRekhta.preprocessing import Preprocessor

text = "Apka service boht achi hai! 😍🔥"

# Remove emojis and punctuation
pre = Preprocessor(lowercase=True, emoji_handling="remove")
cleaned = pre.process(text)
print(cleaned)  # Output: apka service boht achi hai
```

### Emoji Options:

- `"remove"` → Deletes emojis  
- `"replace"` → Converts 😊 → smiling_face  
- `"ignore"` → Leaves emojis untouched

---

## Stopword Removal

```python
from romanRekhta.stopwords import StopwordHandler

# Load from file and extend with custom stopwords
stop_handler = StopwordHandler(
    filepath="stopwords.txt",
    custom_stopwords={"mera", "nahi"}
)

tokens = ["ye", "mera", "kaam", "nahi", "acha", "hai"]
filtered = stop_handler.remove_stopwords(tokens)
print(filtered)  # Output: ['ye', 'kaam', 'acha']

# Load only from file
stop_handler = StopwordHandler(filepath="stopwords.txt")
tokens = ["ye", "bohat", "acha", "kaam", "hai"]
filtered = stop_handler.remove_stopwords(tokens)
print(filtered)  # Output: ['ye', 'bohat', 'acha', 'kaam']

# Custom stopword list only
custom_words = {"mera", "tumhara"}
stop_handler = StopwordHandler(custom_stopwords=custom_words)
tokens = ["ye", "mera", "bohat", "acha", "kaam", "nahi"]
filtered = stop_handler.remove_stopwords(tokens)
print(filtered)  # Output: ['ye', 'bohat', 'acha', 'kaam']

# Combine file + custom stopwords
stop_handler = StopwordHandler(
    filepath="stopwords.txt",
    custom_stopwords={"nahi", "kya"}
)
tokens = ["ye", "nahi", "kya", "acha", "kaam"]
filtered = stop_handler.remove_stopwords(tokens)
print(filtered)  # Output: ['ye', 'acha', 'kaam']
```

---

## Tokenization

```python
from romanRekhta.tokenizer import word_tokenize, sentence_tokenize

text = "Yeh idea bohat acha hai. Shukriya!"

# Word tokenization
tokens = word_tokenize(text)
print(tokens)  # ['Yeh', 'idea', 'bohat', 'acha', 'hai', 'Shukriya']

# Sentence tokenization
sentences = sentence_tokenize(text)
print(sentences)  # ['Yeh idea bohat acha hai', ' Shukriya']

# Advanced tokenization method
tokens = word_tokenize(text, method="regex")
```

---

## Configurable Preprocessor Options

| Option                   | Type | Default | Description                                  |
|--------------------------|------|---------|----------------------------------------------|
| `lowercase`              | bool | True    | Convert to lowercase                         |
| `punctuation`            | bool | True    | Remove punctuation                           |
| `emoji_handling`         | str  | remove  | Options: `'remove'`, `'replace'`, `'ignore'` |
| `normalize_space`        | bool | True    | Remove extra whitespaces                     |
| `remove_non_ascii_chars` | bool | False   | Remove emojis and symbols                    |

---

## File-Based Stopwords

Place a `stopwords.txt` file in your project or repository.  
Each line should contain **one Roman Urdu stopword**.

---

## Contributing

We welcome contributors to improve this library! Here’s how you can help:

-  Add more Roman Urdu stopwords to `stopwords.txt`
-  Suggest or implement new features (normalization, spell checker, sentiment analysis)
-  Report bugs or edge cases

### To contribute:

1. Fork the repo  
2. Create a new branch  
3. Commit your changes  
4. Submit a Pull Request

---

Made with ❤️ in Pakistan 🇵🇰 for the Roman Urdu NLP community.
