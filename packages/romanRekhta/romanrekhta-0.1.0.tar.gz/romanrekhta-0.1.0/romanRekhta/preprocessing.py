import re
import string
import emoji


def to_lowercase(text: str) -> str:
    """
    Converts the input text to lowercase.
    """
    return text.lower()


def remove_punctuation(text: str) -> str:
    """
    Removes punctuation from the text using string.punctuation.
    """
    return text.translate(str.maketrans('', '', string.punctuation))


def remove_emojis(text: str) -> str:
    """
    Removes emojis from the text.
    """
    return emoji.replace_emoji(text, replace='')


def replace_emojis_with_text(text: str) -> str:
    """
    Replaces emojis with descriptive text labels.
    """
    return emoji.demojize(text, delimiters=(" ", " "))


def normalize_whitespace(text: str) -> str:
    """
    Removes extra spaces and trims leading/trailing spaces.
    """
    return re.sub(r'\s+', ' ', text).strip()


def remove_non_ascii(text: str) -> str:
    """
    Removes non-ASCII characters (optional).
    """
    return re.sub(r'[^\x00-\x7F]+', '', text)


class Preprocessor:
    """
    A customizable Roman Urdu text preprocessor.
    """

    def __init__(
        self,
        lowercase: bool = True,
        punctuation: bool = True,
        emoji_handling: str = "remove",  # options: "remove", "replace", "ignore"
        normalize_space: bool = True,
        remove_non_ascii_chars: bool = True
    ):
        """
        Args:
            lowercase (bool): Convert text to lowercase
            punctuation (bool): Remove punctuation
            emoji_handling (str): One of "remove", "replace", "ignore"
            normalize_space (bool): Normalize whitespace
            remove_non_ascii_chars (bool): Strip non-ASCII characters
        """
        self.lowercase = lowercase
        self.punctuation = punctuation
        self.emoji_handling = emoji_handling
        self.normalize_space = normalize_space
        self.remove_non_ascii_chars = remove_non_ascii_chars

    def process(self, text: str) -> str:
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        if self.lowercase:
            text = to_lowercase(text)

        if self.punctuation:
            text = remove_punctuation(text)

        if self.emoji_handling == "remove":
            text = remove_emojis(text)
        elif self.emoji_handling == "replace":
            text = replace_emojis_with_text(text)

        if self.remove_non_ascii_chars:
            text = remove_non_ascii(text)

        if self.normalize_space:
            text = normalize_whitespace(text)

        return text
