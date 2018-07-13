import re
import string
from nltk.tokenize import RegexpTokenizer

class Tokenize():
    def WordTokenize(self, sentence, stopword=None, removepunct=False, splitby='space'):
        """ Tokenize sentence into words
        Parameters:
            sentence - text of string
            stopword - list of unnecessary words
            removepunct - punctuation
            splitby - split sentence based on
        Returns: a list of words
        """
        if splitby.strip().lower()=='space':
            words = re.split(r'\s',sentence)
        elif splitby.strip().lower()=='word':
            words = re.split('(\w+)?', sentence)
        else:
            raise NotImplementedError

        # S:jika remove punct true : hapus tanda baca
        if removepunct:
            remove = string.punctuation
            remove = remove.replace("-", "")
            transtab = str.maketrans('', '', remove)
            words = [w.translate(transtab).strip() for w in words]
            # E:jika remove punct true : hapus tanda baca

            # Hapus seluruh empty char pada list
            words = [w.strip().lower() for w in words if w.strip()]

            # S: Hapus stopword
            # stopword = ['memang']
            # words = filter(lambda x: x not in stopword, words) # Hapus kata yang berada dalam stopwords
            # E: Hapus stopword

        return words

    def CharTokenize(self,word):
        """ Tokenize word into characters
        Parameters:
            word - text of String
        Returns: a list of characters
        """
        return list(word)
