from .config import Config
from .lemmatizetoken import LemmatizeTokens
from .tokenizer import Tokenizer
from .pybotrie import PyBoTrie
from .bosyl import BoSyl
from .pybotextchunks import PyBoTextChunks


class BoTokenizer:
    """
    Convenience class to tokenize a given string.

    """
    def __init__(self, profile, toadd_filenames=[], todel_filenames=[], lemma_folder=None, ignore_chars=[]):
        """
        :param profile: profile for building the trie. (see config.yaml)
        """
        self.config_profile = Config("pybo.yaml")
        self.ignore_chars = ignore_chars
        self.lt = LemmatizeTokens(lemma_folder=lemma_folder)
        self.tok = Tokenizer(PyBoTrie(BoSyl(),
                                      profile=profile,
                                      toadd_filenames=toadd_filenames,
                                      todel_filenames=todel_filenames,
                                      config=self.config_profile
                                      )
                             )

    def tokenize(self, string, split_affixes=True, lemmatize=True, phono=False, debug=False):
        """
        :param string: to be tokenized
        :param split_affixes: separates the affixed particles into seperate tokens if True
        :return: list of pybo.tokenizer.Token objects
        """
        preprocessed = PyBoTextChunks(string, ignore_chars=self.ignore_chars)
        tokens = self.tok.tokenize(preprocessed, split_affixes=split_affixes, phono=phono, debug=debug)
        if lemmatize:
            self.lt.lemmatize(tokens)
        return tokens
