from collections import defaultdict, Counter
import numpy as np
import pandas as pd

class LanguageNgramModel:
    """
    The model remembers and predicts which letters follow which.
    Constructor parameters:
        order - number of characters the model remembers, or n-1
        smoothing - the number, added to each counter for stability
        recursive - weight of the model of one order less
    Learned parameters:
        counter_ - storage of n-grams, as dict of counters
        vocabulary_ - set of characters that the model knows
    """
    def __init__(self, order=1, smoothing=1.0, recursive=0.001):
        self.order = order
        self.smoothing = smoothing
        self.recursive = recursive

    def fit(self, corpus):
        """ Estimate freqency of all n-grams in the text
        parameters:
            corpus - a text string
        """
        self.counter_ = defaultdict(lambda: Counter())
        self.vocabulary_ = set()
        for i, token in enumerate(corpus[self.order:]):
            context = corpus[i:(i+self.order)]
            self.counter_[context][token] += 1
            self.vocabulary_.add(token)
        self.vocabulary_ = sorted(list(self.vocabulary_))
        if self.recursive > 0 and self.order > 0:
            self.child_ = LanguageNgramModel(self.order-1, self.smoothing, self.recursive)
            self.child_.fit(corpus)

    def get_counts(self, context):
        """ Estimate frequency of all symbols that may follow the context
        Parameters:
            context - text string (only the last self.order chars matter)
        Returns:
            freq - vector of letter conditional frequencies, as pandas.Series
        """
        if self.order:
            local = context[-self.order:]
        else:
            local = ''
        freq_dict = self.counter_[local]
        freq = pd.Series(index=self.vocabulary_)
        for i, token in enumerate(self.vocabulary_):
            freq[token] = freq_dict[token] + self.smoothing
        if self.recursive > 0 and self.order > 0:
            child_freq = self.child_.get_counts(context) * self.recursive
            freq += child_freq
        return freq

    def predict_proba(self, context):
        """ Estimate probability of all symbols that may follow the context
        Parameters:
            context - text string (only the last self.order chars matter)
        Returns:
            freq - vector of letter conditional frequencies, as pandas.Series
        """
        counts = self.get_counts(context)
        return counts / counts.sum()

    def single_log_proba(self, context, continuation):
        """ Estimate log probability of the certain continuation of the context
        Parameters:
            context - text string, known beginning of the phrase
            continuation - text string, its hypothetical end
        Returns:
            result - a float, log of probability
        """
        result = 0.0
        for token in continuation:
            result += np.log(self.predict_proba(context)[token])
            context += token
        return result

    def single_proba(self, context, continuation):
        """ Estimate probability of the certain continuation of the context
        Parameters:
            context - text string, known beginning of the phrase
            continuation - text string, its hypothetical end
        Returns:
            result - a float, probability
        """
        return np.exp(self.single_log_proba(context, continuation))
