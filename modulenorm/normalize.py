from modulenorm.LanguageNgramModel import LanguageNgramModel
from modulenorm.MissingLetterModel import MissingLetterModel
from heapq import heappush, heappop
import re
import numpy as np

character = ['.',',',';',':','-,','...','?','!','(',')','[',']','{','}','<','>','"','/','\'','#','-','@']

class Normalize():

    def remove_ascii_unicode(self, text):
        """ Remove ASCII and Unicode
        Parameters:
            text - text of string
        Returns:
        """
        text = text.encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[^\x00-\x7f]',r'',text)
        return text

    def lower_text(self, text):
        """ Change character into lower case
        Parameters:
            text - text of string
        Returns:
        """
        text = text.lower()
        return text

    def repeat_char_modify(self, text):
        """ Convert repeated character into one character
        Parameters:
            text - text of string
        Returns:
        """
        for i in range(len(character)):
            char_long = 5
            while char_long >= 2:
                char = character[i]*char_long
                text = text.replace(char, character[i])
                char_long -= 1
        return text

    def remove_elipsis(self, text):
        """ Remove elipsis
        Parameters:
            text - text of string
        Returns:
        """
        text = text.replace('...', ' ...')
        text = text.replace(' ...','')
        return text

    def remove_newline(self, text):
        """ Remove newline
        Parameters:
            text - text of string
        Returns:
        """
        text = text.replace('\n', ' ')
        return text

    def remove_url(self, text):
        """ Remove URL http
        Parameters:
            text - text of string
        Returns:
        """
        text = re.sub(r"\s—\s", "", text)
        text = re.sub(r"http\S+", "", text)
        return text

    def remove_emoticons(self, text):
        """ Remove emoticon
        Parameters:
            text - text of string
        Returns:
        """
        smileys_pattern = re.compile(r"(?:X|:|;|=)(?:-)?(?:\)|\(|O|D|P|S){1,}", re.IGNORECASE)
        return smileys_pattern.sub(r'', text)

    def remove_hashtags_mentions(self, text):
        """ Remove hastags and mentions
        Parameters:
            text - text of string
        Returns: text of string
        """
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ", text).split())

    def remove_rt_fav(self, text):
        """ Remove RT and FAV
        Parameters:
            text - text of string
        Returns:
        """
        text = re.sub(r'^(RT|FAV)','', text)
        return text

    def generate_options(self, prefix_proba, prefix, suffix,
                     lang_model, missed_model, optimism=0.5, cache=None):
        """ Generate partial options of abbreviation decoding (a helper function)
        Parameters:
            prefix_proba - log probability of decoded part of the abbreviation
            prefix - decoded part of the abbreviation
            suffix - not decoded part of the abbreviation
            lang_model - the language model
            missed_model - the abbreviation probability model
            optimism - coefficient for log likelihood of the word end
            cache - storage of suffix likelihood estimates
        Returns: list of options in the form (likelihood estimate, decoded part,
            not decoded part, the new letter, the suffix likelihood estimate)
        """
        options = []
        for letter in lang_model.vocabulary_ + ['']:
            if letter:  # here we assume the character was missing
                next_letter = letter
                new_suffix = suffix
                new_prefix = prefix + next_letter
                proba_missing_state = - np.log(missed_model.predict_proba(prefix, letter))
            else:  # here we assume there was no missing character
                next_letter = suffix[0]
                new_suffix = suffix[1:]
                new_prefix = prefix + next_letter
                proba_missing_state = - np.log((1 - missed_model.predict_proba(prefix, next_letter)))
            proba_next_letter = - np.log(lang_model.single_proba(prefix, next_letter))
            if cache:
                proba_suffix = cache[len(new_suffix)] * optimism
            else:
                proba_suffix = - np.log(lang_model.single_proba(new_prefix, new_suffix)) * optimism
            proba = prefix_proba + proba_next_letter + proba_missing_state + proba_suffix
            options.append((proba, new_prefix, new_suffix, letter, proba_suffix))
        return options

    def noisy_channel(self, word, lang_model, missed_model, freedom=3.0,
                  max_attempts=10000, optimism=0.9, verbose=False):
        """ Suggest phrases, for which word may be the abbreviation
        parameters:
            word - string, the abbreviation
            lang_model - the language model
            missed_model - the abbreviation probability model
            freedom - possible quality range of log likelihood of the candidates
            max_attempts - maximum number of iterations
            optimism - coefficient for log likelihood of the word end
            verbose - whether to print current candidates in the runtime
        returns: dict of keys - suggested phrases, and values -
            minus log likelihood of candidates
            The less this value, the more likely the suggestion
        """
        query = word + str(' ')
        prefix = ' '
        prefix_proba = 0.0
        suffix = query
        full_origin_logprob = -lang_model.single_log_proba(prefix, query)
        no_missing_logprob = -missed_model.single_log_proba(prefix, query)
        best_logprob = full_origin_logprob + no_missing_logprob
        # add an empty prefix to the heap
        heap = [(best_logprob * optimism, prefix, suffix, '', best_logprob * optimism)]
        # add the default candidate (without missing characters)
        candidates = [(best_logprob, prefix + query, '', None, 0.0)]
        if verbose:
            print('baseline score is', best_logprob)
        # prepare storage of the phrase suffix probabilities
        cache = {}
        for i in range(len(query)+1):
            future_suffix = query[:i]
            cache[len(future_suffix)] = -lang_model.single_log_proba('', future_suffix) # rough approximation
            cache[len(future_suffix)] += -missed_model.single_log_proba('', future_suffix) # at least add missingness

        for i in range(max_attempts):
            if not heap:
                break
            next_best = heappop(heap)
            if verbose:
                print(next_best)
            if next_best[2] == '':  # the phrase is fully decoded
                # if the phrase is good enough, add it to the answer
                if next_best[0] <= best_logprob + freedom:
                    candidates.append(next_best)
                    # update estimate of the best likelihood
                    if next_best[0] < best_logprob:
                        best_logprob = next_best[0]
            else: # # the phrase is not fully decoded - generate more options
                prefix_proba = next_best[0] - next_best[4] # all proba estimate minus suffix
                prefix = next_best[1]
                suffix = next_best[2]
                new_options = self.generate_options(
                    prefix_proba, prefix, suffix, lang_model,
                    missed_model, optimism, cache)
                # add only the solution potentially no worse than the best + freedom
                for new_option in new_options:
                    if new_option[0] < best_logprob + freedom:
                        heappush(heap, new_option)
        if verbose:
            print('heap size is', len(heap), 'after', i, 'iterations')
        result = {}
        for candidate in candidates:
            if candidate[0] <= best_logprob + freedom:
                result[candidate[1][1:-1]] = candidate[0]
        return result
