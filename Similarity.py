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

for number in tqdm(range(1, len(df))):
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

dfInd = df[["5", "KSIC", "count", "vector", "10"]]
dfInd = dfInd[dfInd["KSIC"].isna() == False]
dfInd["KSIC2"] = [x[0:2] for x in dfInd["KSIC"]]

dfCount = dfInd.groupby(["KSIC2", "5"]).agg("count").reset_index()
excluding = []
for ind in set(dfCount["KSIC2"]):
    data = dfCount[dfCount["KSIC2"] == ind]
    for number in data["KSIC"]:
        if number < 5:
            excluding.append(ind)
            break
excluding.sort()

dfInd["KSIC3"] = [1 if x in excluding else 0 for x in dfInd["KSIC2"]]
dfInd2 = dfInd[dfInd["KSIC3"] == 0]
del df, data, df_ind, dfCount, excluding, ind, number, dfInd

dfInd2 = dfInd2.sort_values(['KSIC2', '5'], ascending=[True, True])
dfInd2 = dfInd2[dfInd2["10"].isna() == False]  # 법인등록번호 누락 제거 

yearend = list(set(dfInd2["5"]))
yearend.sort()
ind = list(set(dfInd2["KSIC2"]))
ind.sort()

indSim = []
for industry in tqdm(ind, desc="Industry"):
    for ye in tqdm(yearend, desc="Year End", leave=False):
        vec = dfInd2[dfInd2["5"] == ye]
        vec = vec[vec["KSIC2"] == industry]
        keyBox = []
        for i in range(len(vec)):
            for j in range(len(vec)):
                loopItem = []
                
                if vec.iloc[i,4] != vec.iloc[j,4]:  # 업종내 다른 기업과 비교
                    key = [vec.iloc[i,4], vec.iloc[j,4]]
                    key.sort()
                    key = tuple(key)
                    if key not in keyBox:
                        keyBox.append(key)
                        sim = cosine_similarity(vec.iloc[i,3], vec.iloc[j,3])
                
                        output = sim[0][0]
                        loopItem.append(key)
                        loopItem.append(industry)
                        loopItem.append(ye)
                        loopItem.append(output)
                        loopItem.append(np.maximum([vec.iloc[i,2]], [vec.iloc[j,2]])[0])
                        
                        indSim.append(loopItem)

df = pd.DataFrame(indSim, columns=["key", "ksic", "yearend", "sim", "count"])
df.to_csv("indsim.txt")
df["key"] = [tuple(x) for x in df["key"]]
df2 = df.drop_duplicates(subset=["key"])
df2.to_csv("indsim2.txt")
