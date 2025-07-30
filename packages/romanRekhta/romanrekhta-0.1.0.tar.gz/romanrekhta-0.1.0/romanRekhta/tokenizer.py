import re
from typing import List

def word_tokenize(text: str, method: str = "whitespace") -> List[str]:
    """
    Tokenizes input text into words.

    Args:
        text (str): Input string
        method (str): Tokenization method: 'whitespace' or 'regex'

    Returns:
        list of str: Tokens
    """
    if method == "regex":
        return re.findall(r"\b\w+\b", text.lower())
    elif method == "whitespace":
        return text.strip().split()
    else:
        raise ValueError("Invalid tokenization method. Choose 'whitespace' or 'regex'")


def sentence_tokenize(text: str) -> List[str]:
    """
    Splits input text into sentences based on punctuation.
    (Basic – can be replaced later with model-based sentence segmentation)

    Args:
        text (str): Input paragraph

    Returns:
        list of str: Sentences
    """
    return re.split(r'[.!?]+', text.strip())
