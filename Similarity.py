# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 10:57:09 2021

@author: yoonseok
"""

import os
import pandas as pd
import pickle
from tqdm import tqdm
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

# data preprocessing
os.chdir(r"C:\data")

df = pd.read_csv("preprocessedDocumentsOut.txt")
df = df.dropna()  # Nan 제거
df["documents"].str.strip()  # Whitespace 제거
df["count"] = df["documents"].str.len()  # string 수 
df = df[df["count"] > 100]  # 입력내용이 1을 초과하는 입력값   

with open("tfIdfVec_twitter_noun_trigram.pkl", 'rb') as inp:
    vectors = pickle.load(inp)

df["vector"] = [np.reshape(x, (1, vectors.shape[1])) for x in tqdm(vectors.toarray())]

df = df.drop(["documents"], axis=1)
del vectors, inp

df_ind = pd.read_excel("industry.xlsx", dtype={'KSIC': str}, sheet_name='data')
df = df.rename(columns={"11": "INDUSTRY"})

df = pd.merge(df, df_ind, on = "INDUSTRY", how ='left')

df["floatYE"] = [float(x.replace("(","").replace(")","")) for x in df["5"]]

simList = []
simList.append(999)

for number in tqdm(range(1,36666)):
    sim = cosine_similarity(df["vector"][number], df["vector"][number-1])
    if df["10"][number] == df["10"][number-1] and df["floatYE"][number] == df["floatYE"][number-1]+1 :
        sim = cosine_similarity(df["vector"][number], df["vector"][number-1])
        simList.append(sim[0][0])
    else:
        simList.append(999)

df["year-to-year"] = simList

dfYear = df[["5", "10", "KSIC", "count", "year-to-year"]]
dfYear = dfYear[dfYear["year-to-year"] != 999]

dfYear.to_csv("year-to-year.txt")
