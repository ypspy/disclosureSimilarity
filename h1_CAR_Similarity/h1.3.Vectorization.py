# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 13:01:18 2021

@author: yoonseok
"""


from ckonlpy.tag import Twitter
from collections import defaultdict

import os
import pandas as pd
import numpy as np
import re
from tqdm import tqdm

from sklearn.feature_extraction.text import TfidfVectorizer
import pickle


### n-gram 토크나이저 lovit/soynlp 참조 https://lovit.github.io/nlp/2018/10/23/ngram/

class NgramTokenizer:
 
    def __init__(self, ngrams, base_tokenizer, n_range=(1, 3)):
        self.ngrams = ngrams
        self.base_tokenizer = base_tokenizer
        self.n_range = n_range

    def __call__(self, sent):
        return self.tokenize(sent)

    def tokenize(self, sent):
        if not sent:
            return []

        unigrams = self.base_tokenizer.tokenize(sent)  # pos(sent, join=True)

        n_begin, n_end = self.n_range
        ngrams = []
        for n in range(n_begin, n_end + 1):
            for ngram in self._to_ngrams(unigrams, n):
                ngrams.append('-'.join(ngram))
        return ngrams

    def _to_ngrams(self, words, n):
        ngrams = []
        for b in range(0, len(words) - n + 1):
            ngram = tuple(words[b:b+n])
            if ngram in self.ngrams:
                ngrams.append(ngram)
        return ngrams

def get_ngram_counter(dataframe, base_tokenizer, min_count=10, n_range=(1,5)):
    """
    리스트/Array가 들어오는데, 요소는 string이다.
    """
    def to_ngrams(words, n):
        ngrams = []
        for b in range(0, len(words) - n + 1):
            ngrams.append(tuple(words[b:b+n]))
        return ngrams

    n_begin, n_end = n_range
    ngram_counter = defaultdict(int)
    for doc in tqdm(dataframe, desc="N-Gram Identification"):
        words = base_tokenizer.tokenize(doc)  # Twitter의 경우 tokenize/그 외 pos

        for n in range(n_begin, n_end + 1):
            ngramList = to_ngrams(words, n)

            for ngram in ngramList:  
                ngram_counter[ngram] += 1

    ngram_counter = {
        ngram:count for ngram, count in ngram_counter.items()
        if count >= min_count
    }

    return ngram_counter

###

class TwitterMod():
    """
    cKonlpy의 twitter에는 join이 없다. 단일 목적 클래스. twitter를 집어넣어서 object를 만든다.
    리스트/Array가 들어오는데, 요소는 string이다. object를 만들때, noun=True를 하면 명사만 반환한다.
    반환은 리스트/Array이고 요소는 tag가 join된 형태소의 리스트이다. 불용어를 제거하지 않으려면 stopword=False.
    """
    
    def __init__(self, base_tokenizer, stopwords, noun=False):
        self.base_tokenizer = base_tokenizer
        self.noun = noun
        self.stopwords = stopwords

    def __call__(self, sent):
        return self.tokenize(sent)

    def tokenize(self, sent, pos=True):

        container, container2 = [], []
        
        for words in self.base_tokenizer.pos(sent):
            if self.noun:
                if words[1] == "Noun":
                    container2.append("{0}/{1}".format(words[0], words[1]))
            else:
               container2.append("{0}/{1}".format(words[0], words[1])) 
        container.append(container2)
        container = removeStopword(container, self.stopwords)
                
        if len(container) == 1:
            container = container[0]
        
        return container

def preprocessString(string):
    p = re.compile('[^ ㄱ-ㅣ가-힣A-Za-z]+')
    string = p.sub(' ', string)
    string = string.strip()  # 문서 앞뒤 공백 제거
    string = ' '.join(string.split())  # Replace Multiple whitespace into one
    return string

def removeStopword(dataframe, stopword):
    stopword = stopWord.stopword.to_list()
    container = []
    for packages in dataframe:
        container2 = []
        for words in packages:            
            if words not in stopword:
                container2.append(words)                    
        container.append(container2)
    return container


# Create Tokenizer object
os.chdir(r"C:\analytics")
stopWord = pd.read_csv("dataset7.stopwords.csv", names=["stopword"])
twitter_Konlpy = Twitter()
twitter = TwitterMod(twitter_Konlpy, stopWord, noun=True)

# data preprocessing
os.chdir(r"C:\data")

df = pd.read_csv("h1.preprocessedDocumentsOut_FS.txt")

df["documents"].str.strip()  # Whitespace 제거
df["count"] = df["documents"].str.len()  # string 수 
df = df[df["count"] > 100]  # 입력내용이 100을 초과하는 텍스트만 사용   

# N-gram Tuning
n_range=(1,3)
ngram_counter = get_ngram_counter(df["documents"], twitter, min_count=100, n_range=n_range)
ngram_tokenizer = NgramTokenizer(ngram_counter, twitter, n_range=n_range)

# n-gram Vectorizer
vectorizer = TfidfVectorizer(tokenizer = ngram_tokenizer,
                             lowercase = False,
                             )
vec = vectorizer.fit_transform(tqdm(df["documents"], desc="Fit and Transform"))  
df["vector"] = [np.reshape(x, (1, vec.shape[1])) for x in tqdm(vec.toarray())]

with open("h1.tfIdfVec_twitter_noun_trigram.pkl", 'wb') as output:
    pickle.dump(vec, output, pickle.HIGHEST_PROTOCOL)

# pickle로 vector만 빼낸다
