from collections import defaultdict, Counter
import numpy as np
import pandas as pd

class MissingLetterModel:
    """
    The model remembers and predicts which letters are usually missed.
    Constructor parameters:
        order - number of characters the model remembers, or n-1
        smoothing_missed - the number added to missed counter
        smoothing_total - the number added to total counter
    Learned parameters:
        missed_counter_ - counter of occurences of the missed characters
        total_counter_ - counter of occurences of all characters
    """
    def __init__(self, order=0, smoothing_missed=0.3, smoothing_total=1.0):
        self.order = order
        self.smoothing_missed = smoothing_missed
        self.smoothing_total = smoothing_total

    def fit(self, sentence_pairs):
        """ Estimate of missing probability for each symbol
        Parameters:
            sentence_pairs - list of (original phrase, abbreviation)
        In the abbreviation, all missed symbols are replaced with "-"
        """
        self.missed_counter_ = defaultdict(lambda: Counter())
        self.total_counter_ = defaultdict(lambda: Counter())
        for (original, observed) in sentence_pairs:
            for i, (original_letter, observed_letter) \
                    in enumerate(zip(original[self.order:], observed[self.order:])):
                context = original[i:(i+self.order)]
                if observed_letter == '-':
                    self.missed_counter_[context][original_letter] += 1
                self.total_counter_[context][original_letter] += 1

    def predict_proba(self, context, last_letter):
        """ Estimate of probability of last_letter being missed after context"""
        if self.order:
            local = context[-self.order:]
        else:
            local = ''
        missed_freq = self.missed_counter_[local][last_letter] + self.smoothing_missed
        total_freq = self.total_counter_[local][last_letter] + self.smoothing_total
        return missed_freq / total_freq

    def single_log_proba(self, context, continuation, actual=None):
        """ Estimate log probability that after context,
            continuation is abbreviated to actual.
        If actual is None, it is assumed that nothing is abbreviated.
        """
        if not actual:
            actual = continuation
        result = 0.0
        for orig_token, act_token in zip(continuation, actual):
            pp = self.predict_proba(context, orig_token)
            if act_token != '-':
                pp = 1 - pp
            result += np.log(pp)
            context += orig_token
        return result

    def single_proba(self, context, continuation, actual=None):
        """ Estimate probability that after context,
            continuation is abbreviated to actual.
        If actual is None, it is assumed that nothing is abbreviated.
        """
        return np.exp(self.single_log_proba(context, continuation, actual))
