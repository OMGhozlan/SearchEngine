from glob import glob
from nltk.stem.porter import *
from operator import itemgetter
from nltk.corpus import stopwords
from collections import defaultdict

class SearchWord(object):
    def __init__(self, ngram_size=3, len_variance=1, words=set([w.lower() for w in open('E:/Final/word_list.en').read().splitlines()])):
        self.ngram_size = ngram_size
        self.len_variance = len_variance
        self.words = words
		
        # create dictionary of ngrams and the words that contain them
        self.ngram_words = defaultdict(set)
        for word in self.words:
            for ngram in self.ngrams(word):
                self.ngram_words[ngram].add(word)

    def find(self, word):
        return word in self.words

    def jaccard(self, word, target_word):
        word = set(list(word))
        target_word = set(list(target_word))
        return float(len(word & target_word)) / len(word | target_word)		

    def ngrams(self, word):
        all_ngrams = set()
        for i in range(0, len(word) - self.ngram_size + 1):
            all_ngrams.add(word[i:i + self.ngram_size])
        return all_ngrams

    def suggested(self, target_word, results=10):
        word_ranking = defaultdict(int)
        possible_words = set()
        for ngram in self.ngrams(target_word):
            words = self.ngram_words[ngram]
            for word in words:
                if len(word) >= len(target_word) - self.len_variance and \
                   len(word) <= len(target_word) + self.len_variance:
                    word_ranking[word] += 1
        # Descending
        ranked_word_pairs = sorted(word_ranking.items(), key=itemgetter(1), reverse=True)
        return [word_pair[0] for word_pair in ranked_word_pairs[0:results]]
		
    def spell(self, word, results=5):
        dist = []
        suggested = self.suggested(word)
        for s_word in suggested:
            dist += [self.jaccard(s_word, word)]
        return [sug for _, sug in sorted(zip(dist, suggested), reverse=True)][0:results]
		
    def soundex(self, text):
        text = text.upper()
        soundex = ""
        soundex += text[0]
        mapping = {"BFPV": "1", "CGJKQSXZ": "2", "DT": "3", "L": "4", "MN": "5", "R": "6", "AEIOUWHY": "."}
        for char in text[1:]:
            for key in mapping.keys():
                if char in key:
                    code = mapping[key]
                    if code != soundex[-1]:
                        soundex += code

        soundex = soundex.replace(".", "")
        soundex = soundex[:4].ljust(4, "0")
        return soundex


def punc_remove(text):
    from string import punctuation
    unpunked = ""
    punc = set(punctuation)

    for i in range(len(text)):
        if (text[i] in punc):
            continue
        else:
            unpunked += text[i]
    return unpunked


def word_stemmer(text):
    words = []
    stemed_words = []
    for line in text.split('\n'):
        for word in line.split():
            words.append(word)
    stemmer = PorterStemmer()
    for word in words:
        stemed_words.append(stemmer.stem(word))
    return stemed_words


def remove_stop_words(words):
    new_words = []
    stopwrds = stopwords.words('english')
    for word in words:
        if word.lower() not in stopwrds:
            new_words.append(word.lower())
    return new_words

def tokenize(text):
	text = punc_remove(text)
	text = remove_stop_words(text)
	text = word_stemmer(text)
	return text