import pickle
from glob import glob
from functools import reduce
from collections import Counter
from pprint import pprint as Print

def parse_files(files='*.txt'):
	text, words = {}, set()
	for file in glob(files):
		# print(file)
		with open(file, 'r', encoding='utf-8') as f:
			t = f.read().split() #encode('latin1').decode('cp1252').split()
			words |= set(t)
			text[file.split('\\')[-1].strip()] = t
	return text, words


def build_index():
	invidx = {word:set((text_, word_index)
						  for text_, wrds in text.items()
						  for word_index in (i for i,w in enumerate(wrds) if word==w)
						  if word in wrds)
				 for word in words}
	return {k:sorted(v) for k,v in invidx.items()}



def save_index():
	with open('./w_database.txt', 'wb') as pickler:
	  pickle.dump(invidx, pickler)

def read_index():
	with open('./w_database.txt', 'rb') as pickler:
	  invidx = pickle.loads(pickler.read())	

def read_index_():
	with open('./w_database.txt', 'rb') as pickler:
	  return pickle.loads(pickler.read())	
	  
print("[*] Building index...")	
text, words = parse_files('./Files/*.txt')	
"""invidx = {word:set((text_, word_index)
                      for text_, wrds in text.items()
                      for word_index in (i for i,w in enumerate(wrds) if word==w)
                      if word in wrds)
             for word in words}
-invidx = {k:sorted(v) for k,v in invidx.items()}"""
invidx = read_index_()
print("[*] Done!")

def get_terms(terms):
	if not set(terms).issubset(words):
		return set()
	return reduce(set.intersection, (set(i[0] for i in t_idx) for term, t_idx in invidx.items() if term in terms), set(text.keys()))

def search(sentence):
    words = sentence.strip().split()
    if not set(words).issubset(words):
        return set()
    firstword, *otherwords = words
    found = []
    for term in get_terms(words):
        for firstindx in (indx for t,indx in invidx[firstword]
                          if t == term):
            if all( (term, firstindx + 1 + otherindx) in invidx[otherword]
                    for otherindx, otherword in enumerate(otherwords) ):
                found.append(term)
    return found
	
##D:/Users/Threadcount/Desktop/Final/*.txt