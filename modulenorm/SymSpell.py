'''
################

This program is a Python version of a spellchecker based on SymSpell,
a Symmetric Delete spelling correction algorithm developed by Wolf Garbe
and originally written in C#.

From the original SymSpell documentation:

"The Symmetric Delete spelling correction algorithm reduces the complexity
 of edit candidate generation and dictionary lookup for a given Damerau-
 Levenshtein distance. It is six orders of magnitude faster and language
 independent. Opposite to other algorithms only deletes are required,
 no transposes + replaces + inserts. Transposes + replaces + inserts of the
 input term are transformed into deletes of the dictionary term.
 Replaces and inserts are expensive and language dependent:
 e.g. Chinese has 70,000 Unicode Han characters!"

For further information on SymSpell, please consult the original
documentation:
  URL: blog.faroo.com/2012/06/07/improved-edit-distance-based-spelling-correction/
  Description: blog.faroo.com/2012/06/07/improved-edit-distance-based-spelling-correction/

The current version of this program will output all possible suggestions for
corrections up to an edit distance (configurable) of max_edit_distance = 3.

With the exception of the use of a third-party method for calculating
Demerau-Levenshtein distance between two strings, we have largely followed
the structure and spirit of the original SymSpell algorithm and have not
introduced any major optimizations or improvements.

################
'''

import re

class SymSpell:
    def __init__(self, max_edit_distance=3, verbose=0, dictionary={}, longest_word_length=0):
        '''
            verbose
            # 0: top suggestion
            # 1: all suggestions of smallest edit distance
            # 2: all suggestions <= max_edit_distance (slower, no early termination)
        '''
        self.max_edit_distance = max_edit_distance
        self.verbose = verbose
        self.dictionary = dictionary
        self.longest_word_length = longest_word_length

    def get_deletes_list(self, w):
        '''given a word, derive strings with up to max_edit_distance characters
           deleted'''
        deletes = []
        queue = [w]
        for d in range(self.max_edit_distance):
            temp_queue = []
            for word in queue:
                if len(word)>1:
                    for c in range(len(word)):  # character index
                        word_minus_c = word[:c] + word[c+1:]
                        if word_minus_c not in deletes:
                            deletes.append(word_minus_c)
                        if word_minus_c not in temp_queue:
                            temp_queue.append(word_minus_c)
            queue = temp_queue

        return deletes

    def create_dictionary_entry(self, w):
        '''add word and its derived deletions to dictionary'''
        # check if word is already in dictionary
        # dictionary entries are in the form: (list of suggested corrections,
        # frequency of word in corpus)
        # global self.longest_word_length
        new_real_word_added = False
        if w in self.dictionary:
            # increment count of word in corpus
            self.dictionary[w] = (self.dictionary[w][0], self.dictionary[w][1] + 1)
        else:
            self.dictionary[w] = ([], 1)
            self.longest_word_length = max(self.longest_word_length, len(w))

        if self.dictionary[w][1]==1:
            # first appearance of word in corpus
            # n.b. word may already be in dictionary as a derived word
            # (deleting character from a real word)
            # but counter of frequency of word in corpus is not incremented
            # in those cases)
            new_real_word_added = True
            deletes = self.get_deletes_list(w)
            for item in deletes:
                if item in self.dictionary:
                    # add (correct) word to delete's suggested correction list
                    self.dictionary[item][0].append(w)
                else:
                    # note frequency of word in corpus is not incremented
                    self.dictionary[item] = ([w], 0)

        return new_real_word_added

    def create_dictionary(self, fname):

        total_word_count = 0
        unique_word_count = 0

        with open(fname) as file:
            print("Creating dictionary...")
            for line in file:
                # separate by words by non-alphabetical characters
                words = re.findall('[a-z]+', line.lower())
                for word in words:
                    total_word_count += 1
                    if self.create_dictionary_entry(word):
                        unique_word_count += 1

        print("total words processed: %i" % total_word_count)
        print("total unique words in corpus: %i" % unique_word_count)
        print("total items in dictionary (corpus words and deletions): %i" % len(self.dictionary))
        print("  edit distance for deletions: %i" % self.max_edit_distance)
        print("  length of longest word in corpus: %i" % self.longest_word_length)

        return self.dictionary

    def dameraulevenshtein(self, seq1, seq2):
        """Calculate the Damerau-Levenshtein distance between sequences.

        This method has not been modified from the original.
        Source: http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/

        This distance is the number of additions, deletions, substitutions,
        and transpositions needed to transform the first sequence into the
        second. Although generally used with strings, any sequences of
        comparable objects will work.

        Transpositions are exchanges of *consecutive* characters; all other
        operations are self-explanatory.

        This implementation is O(N*M) time and O(M) space, for N and M the
        lengths of the two sequences.

        >>> dameraulevenshtein('ba', 'abc')
        2
        >>> dameraulevenshtein('fee', 'deed')
        2

        It works with arbitrary sequences too:
        >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
        2
        """
        # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
        # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
        # However, only the current and two previous rows are needed at once,
        # so we only store those.
        oneago = None
        thisrow = list(range(1, len(seq2) + 1)) + [0]
        for x in range(len(seq1)):
            # Python lists wrap around for negative indices, so put the
            # leftmost column at the *end* of the list. This matches with
            # the zero-indexed strings and saves extra calculation.
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
            for y in range(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)
                # This block deals with transpositions
                if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                    and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                    thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
        return thisrow[len(seq2) - 1]

    def get_suggestions(self, string, silent=False):
        '''return list of suggested corrections for potentially incorrectly
           spelled word'''
        if (len(string) - self.longest_word_length) > self.max_edit_distance:
            if not silent:
                print("no items in dictionary within maximum edit distance")
            return []

        # global self.verbose
        suggest_dict = {}
        min_suggest_len = float('inf')

        queue = [string]
        q_dictionary = {}  # items other than string that we've checked

        while len(queue)>0:
            q_item = queue[0]  # pop
            queue = queue[1:]

            # early exit
            if ((self.verbose<2) and (len(suggest_dict)>0) and
                  ((len(string)-len(q_item))>min_suggest_len)):
                break

            # process queue item
            if (q_item in self.dictionary) and (q_item not in suggest_dict):
                if (self.dictionary[q_item][1]>0):
                # word is in dictionary, and is a word from the corpus, and
                # not already in suggestion list so add to suggestion
                # dictionary, indexed by the word with value (frequency in
                # corpus, edit distance)
                # note q_items that are not the input string are shorter
                # than input string since only deletes are added (unless
                # manual dictionary corrections are added)
                    assert len(string)>=len(q_item)
                    suggest_dict[q_item] = (self.dictionary[q_item][1],
                                            len(string) - len(q_item))
                    # early exit
                    if ((self.verbose<2) and (len(string)==len(q_item))):
                        break
                    elif (len(string) - len(q_item)) < min_suggest_len:
                        min_suggest_len = len(string) - len(q_item)

                # the suggested corrections for q_item as stored in
                # dictionary (whether or not q_item itself is a valid word
                # or merely a delete) can be valid corrections
                for sc_item in self.dictionary[q_item][0]:
                    if (sc_item not in suggest_dict):

                        # compute edit distance
                        # suggested items should always be longer
                        # (unless manual corrections are added)
                        assert len(sc_item)>len(q_item)

                        # q_items that are not input should be shorter
                        # than original string
                        # (unless manual corrections added)
                        assert len(q_item)<=len(string)

                        if len(q_item)==len(string):
                            assert q_item==string
                            item_dist = len(sc_item) - len(q_item)

                        # item in suggestions list should not be the same as
                        # the string itself
                        assert sc_item!=string

                        # calculate edit distance using, for example,
                        # Damerau-Levenshtein distance
                        item_dist = self.dameraulevenshtein(sc_item, string)

                        # do not add words with greater edit distance if
                        # verbose setting not on
                        if ((self.verbose<2) and (item_dist>min_suggest_len)):
                            pass
                        elif item_dist<=self.max_edit_distance:
                            assert sc_item in self.dictionary  # should already be in dictionary if in suggestion list
                            suggest_dict[sc_item] = (self.dictionary[sc_item][1], item_dist)
                            if item_dist < min_suggest_len:
                                min_suggest_len = item_dist

                        # depending on order words are processed, some words
                        # with different edit distances may be entered into
                        # suggestions; trim suggestion dictionary if verbose
                        # setting not on
                        if self.verbose<2:
                            suggest_dict = {k:v for k, v in list(suggest_dict.items()) if v[1]<=min_suggest_len}

            # now generate deletes (e.g. a substring of string or of a delete)
            # from the queue item
            # as additional items to check -- add to end of queue
            assert len(string)>=len(q_item)

            # do not add words with greater edit distance if verbose setting
            # is not on
            if ((self.verbose<2) and ((len(string)-len(q_item))>min_suggest_len)):
                pass
            elif (len(string)-len(q_item))<self.max_edit_distance and len(q_item)>1:
                for c in range(len(q_item)): # character index
                    word_minus_c = q_item[:c] + q_item[c+1:]
                    if word_minus_c not in q_dictionary:
                        queue.append(word_minus_c)
                        q_dictionary[word_minus_c] = None  # arbitrary value, just to identify we checked this

        # queue is now empty: convert suggestions in dictionary to
        # list for output
        if not silent and self.verbose!=0:
            print("number of possible corrections: %i" %len(suggest_dict))
            print("  edit distance for deletions: %i" % self.max_edit_distance)

        # output option 1
        # sort results by ascending order of edit distance and descending
        # order of frequency
        #     and return list of suggested word corrections only:
        # return sorted(suggest_dict, key = lambda x:
        #               (suggest_dict[x][1], -suggest_dict[x][0]))

        # output option 2
        # return list of suggestions with (correction,
        #                                  (frequency in corpus, edit distance)):
        as_list = list(suggest_dict.items())
        outlist = sorted(as_list, key=lambda term_freq_dist: (term_freq_dist[1][1], -term_freq_dist[1][0]))

        if self.verbose==0 and outlist:
            # return only suggestion word
            return outlist[0][0]
        else:
            return outlist

        '''
        Option 1:
        ['file', 'five', 'fire', 'fine', ...]

        Option 2:
        [('file', (5, 0)),
         ('five', (67, 1)),
         ('fire', (54, 1)),
         ('fine', (17, 1))...]
        '''
