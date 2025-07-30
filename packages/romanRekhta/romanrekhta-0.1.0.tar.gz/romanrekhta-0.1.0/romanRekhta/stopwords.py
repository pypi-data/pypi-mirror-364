import os

class StopwordHandler:
    """
    Handles loading and filtering stopwords for Roman Urdu.
    """

    def __init__(self, filepath: str = None, custom_stopwords: set = None):
        """
        Args:
            filepath (str): Path to a .txt file containing stopwords (one per line)
            custom_stopwords (set): Optional override or extension set of stopwords
        """
        self.stopwords = set()

        if filepath and os.path.exists(filepath):
            self._load_from_file(filepath)

        if custom_stopwords:
            self.stopwords.update(custom_stopwords)

    def _load_from_file(self, filepath: str):
        """
        Loads stopwords from a .txt file (one word per line).
        """
        with open(filepath, encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    self.stopwords.add(word)

    def is_stopword(self, word: str) -> bool:
        return word.lower() in self.stopwords

    def remove_stopwords(self, tokens: list) -> list:
        """
        Removes stopwords from a list of tokens.

        Args:
            tokens (list): Tokenized list of words

        Returns:
            list: Cleaned token list
        """
        return [token for token in tokens if not self.is_stopword(token)]


# Convenience function
def remove_stopwords(tokens: list, stopword_handler: StopwordHandler) -> list:
    return stopword_handler.remove_stopwords(tokens)
