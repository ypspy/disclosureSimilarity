# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 13:01:18 2021

@author: yoonseok
"""


from ckonlpy.tag import Twitter

import os
import pandas as pd

import re
from tqdm import tqdm

### n-gram 토크나이저 lovit/soynlp 참조 https://lovit.github.io/nlp/2018/10/23/ngram/

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

length = []

for doc in tqdm(df["documents"], desc="Noun Counting"):
    length.append(len(twitter.tokenize(doc)))

df["length"] = length
df2 = pd.read_csv("h1.similarity.txt")
df3 = pd.merge(df2, df["key", "length"], how="inner", on=["key"])

df3.to_csv("h1.similarity_length.txt")
