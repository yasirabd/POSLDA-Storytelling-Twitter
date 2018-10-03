from collections import Counter
from collections import defaultdict
import random
import numpy as np


class LdaModel:
    """
    Parameters:
        `documents` is the documents which used to find the topics
        `K` is the number of topics
        `alpha` is the hyperparameter for document topic distribution
        `beta` is the hyperparameter for topic word distribution
    """
    def __init__(self, documents=None, K=3, alpha=0.1, beta=0.1, iteration=1000):
        self.documents = documents
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iteration = iteration

        if documents is not None:
            self.trainData()

    def trainData(self):
        """train the data"""
        # a list of Counters, one for each document in documents
        self.document_topic_counts = [Counter() for _ in self.documents]

        # a list of Counters, one for each topic
        self.topic_word_counts = [Counter() for _ in range(self.K)]

        # a list of numbers, one for each topic
        self.topic_counts = [0 for _ in range(self.K)]

        # a list of numbers, one for each document
        self.document_lengths = [len(d) for d in self.documents]

        # the number of distinct words
        distinct_words = set(word for document in self.documents for word in document)
        self.W = len(distinct_words)

        # the number of documents
        self.D = len(self.documents)

        # assigning every word to a random topic, and populating Counter
        random.seed(0)
        self.document_topics = [[random.randrange(self.K) for word in document]
                                for document in self.documents]

        # a list of pwz
        keys = distinct_words
        topics = [k for k in range(self.K)]
        self.pwz_counts = {key: {key: 0 for key in topics} for key in sorted(list(keys))}

        # a list of pzd
        documents = [d for d in range(self.D)]
        self.pzd_counts = {key: {key: 0 for key in topics} for key in documents}

        # a list of word frequency
        self.word_frequencies = {key: {key: 0 for key in documents} for key in sorted(list(keys))}

        for idx, doc in enumerate(self.documents):
            for word in distinct_words:
                self.word_frequencies[word][idx] = self.word_frequencies[word][idx] + doc.count(word)

        for d in range(self.D):
            for word, topic, in zip(self.documents[d], self.document_topics[d]):
                self.document_topic_counts[d][topic] += 1
                self.topic_word_counts[topic][word] += 1
                self.topic_counts[topic] += 1

        # Gibbs Sampling
        # list_perplexity = [0 for x in range(self.iteration)]
        # print(self.W)
        for iter in range(self.iteration):
            # print(iter)
            for d in range(self.D):
                for i, (word, topic) in enumerate(zip(self.documents[d],
                                                      self.document_topics[d])):

                    # remove this word / topic from counts
                    # so that it doesn't influence the weights
                    self.document_topic_counts[d][topic] -= 1
                    self.topic_word_counts[topic][word] -= 1
                    self.topic_counts[topic] -= 1
                    self.document_lengths[d] -= 1

                    # choose a new topic based on the weights
                    new_topic = self.choose_new_topic(d, word, self.K)
                    self.document_topics[d][i] = new_topic

                    # and now add it back to the counts
                    self.document_topic_counts[d][new_topic] += 1
                    self.topic_word_counts[new_topic][word] += 1
                    self.topic_counts[new_topic] += 1
                    self.document_lengths[d] += 1

                    # pwz = self.p_word_given_topic(word, topic, self.beta)
                    # pzd = self.p_topic_given_document(topic, d, self.alpha)
                    # # print("topic", topic, "d", d, "pzd", self.p_topic_given_document(topic, d, self.alpha))
                    # self.pwz_counts[word][topic] = pwz
                    # self.pzd_counts[d][topic] = pzd

            # list_perplexity[iter] = self.perplexity()
            # print(self.perplexity())
            # if iter > 250:
            #     if list_perplexity[iter] - list_perplexity[iter-1] < 0.001:
            #         break

        # get word with pwz
        for d in range(self.D):
            for i, (word, topic) in enumerate(zip(self.documents[d], self.document_topics[d])):
                pwz = self.p_word_given_topic(word, topic, self.beta)
                pzd = self.p_topic_given_document(topic, d, self.alpha)
                # print("topic", topic, "d", d, "pzd", self.p_topic_given_document(topic, d, self.alpha))
                self.pwz_counts[word][topic] = pwz
                self.pzd_counts[d][topic] = pzd

        # print(self.word_frequencies)
        # print()
        # print(self.pwz_counts)
        # print()
        # print(self.pzd_counts)
        # print()
        # print(self.document_topic_counts)

    def perplexity(self):
        # kata frequency
        nkata_list = []
        for i in range(len(self.word_frequencies)):
            result = list(list(self.word_frequencies.values())[i].values())
            nkata_list.append(result)
        nkata_arr = np.array(nkata_list)

        # pwz
        pwz_list = []
        for i in range(len(self.pwz_counts)):
            result = result = list(list(self.pwz_counts.values())[i].values())
            pwz_list.append(result)
        pwz_arr = np.array(pwz_list)

        # pzd
        pzd_list = []
        for i in range(len(self.pzd_counts)):
            result = list(list(self.pzd_counts.values())[i].values())
            pzd_list.append(result)
        pzd_arr = np.transpose(np.array(pzd_list))

        # perplexity
        s = np.matmul(pwz_arr, pzd_arr)
        log_s = np.log10(s, out=np.zeros_like(s), where=(s!=0))
        p_log_s = np.multiply(nkata_arr, log_s)
        sum_p = np.sum(nkata_arr)
        sum_p_log_s = np.sum(p_log_s)
        perplexity = np.exp(-(sum_p_log_s/sum_p))

        return perplexity

    def p_topic_given_document(self, topic, d, alpha):
        """the fraction of words in document _d_
        that are assigned to _topic_ (plus some smoothing)"""

        return ((self.document_topic_counts[d][topic] + alpha) /
                (self.document_lengths[d] + self.K * alpha))

    def p_word_given_topic(self, word, topic, beta):
        """the fration of words assigned to _topic_
        that equal _word_ (plus some smoothing)"""

        return ((self.topic_word_counts[topic][word] + beta) /
                (self.topic_counts[topic] + self.W * beta))

    def topic_weight(self, d, word, k):
        """given a document and a word in that document,
        return the weight for the k-th topic"""

        return self.p_word_given_topic(word, k, self.beta) * self.p_topic_given_document(k, d, self.alpha)

    def sample_from(self, weights):
        """returns i with probability weights[i] / sum(weights)"""

        total = sum(weights)
        rnd = total * random.random()     # uniform between 0 and total
        for i, w in enumerate(weights):
            rnd -= w                      # return the smallest i such that
            if rnd <= 0: return i         # weights[0] + ... + weights[i] >= rnd

    def choose_new_topic(self, d, word, K):
        """returns the new topics"""

        return self.sample_from([self.topic_weight(d, word, k)
                            for k in range(K)])

    def get_pwz(self, word):
        return self.pwz_counts[word]

    def get_topic_word_pwz(self, documents_tagged):
        """return list contains topic, word with tag, and probability word given topic (pwz)"""
        # split the document by space
        documents_tagged_splitted = []
        for t in documents_tagged:
            documents_tagged_splitted.append(t.split(' '))

        distinct_words_tagged = sorted(set(word for document in documents_tagged_splitted for word in document))

        result = []
        for k, word_counts in enumerate(self.topic_word_counts):
            total = 0
            for word, count in word_counts.most_common():
                if count > 0:
                    if total >= 20: break
                    temp = []
                    for word_tagged in distinct_words_tagged:
                        if word == word_tagged.split('/')[0]:
                            temp.append(word_tagged)

                    if len(temp) > 1:
                        for t in temp:
                            result.append([k, t, self.get_pwz(word)[k]])
                            total += 1
                    else:
                        result.append([k, ''.join(temp), self.get_pwz(word)[k]])
                        total += 1
        return result

    def print_topics(self):
        for k, word_counts in enumerate(self.topic_word_counts):
            for word, count in word_counts.most_common():
                if count > 0: print (k, word, count)

    def print_topics2(self):
        topic_names = ["Topik 0: ",
                       "Topik 1: ",
                       "Topik 2: ",
                       "Topik 3: "]
        for document, topic_counts in zip(self.documents, self.document_topic_counts):
            print(document)
            for topic, count, in topic_counts.most_common():
                if count > 0:
                    print(topic_names[topic], count)

    def insert_into_Ccon(self, Ccon, doc_tup):
        """
            print word and what topic are their
        """
        for k, word_counts in enumerate(self.topic_word_counts):

            Ccon["topic "+str(k)] = defaultdict(list)
            for word, count in word_counts.most_common():
                # if count > 0: print ("topic", k, word, count)
                if count > 0:
                    for doc in doc_tup:
                        for w in doc:
                            if word == w[0]:
                                Ccon["topic "+str(k)][w[1]].append(word)
        for key in Ccon:
            for k in Ccon[key]:
                Ccon[key][k] = list(set(Ccon[key][k]))
        print(Ccon)
