# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 12:04:37 2021

@author: yoonseok
"""

import os
import pandas as pd
from tqdm import tqdm

# 1. 작업 폴더로 변경
os.chdir("C:\data\stockinfo\\")  # 작업 폴더로 변경

def GenerateDataFrame(year):
    df = pd.read_csv('stockPrice_' + str(year) + '.csv', dtype=str)
    df = df.rename(columns={"14": "date"})
    # df["date"] = df["date"].astype(int)
    df = df[df["date"].isna() == False]
    return df

dfM = pd.read_csv("ECOS_TABLE_20210907_124001.csv", dtype=str)
dfM["R_mt"] = dfM["R_mt"].astype(float)
dfM["R_mt"] = dfM["R_mt"].round(decimals=4)
dfM = dfM[dfM["date"].isna() == False]

dfM["date"] = [x.strip() for x in dfM["date"]]

for t in tqdm(range(6, 7)):
    df_0 = GenerateDataFrame(1997 + t)
    df_1 = GenerateDataFrame(1998 + t)
    df_2 = GenerateDataFrame(1999 + t)
    
    df_0_1 = df_0[df_0["date"] == str(df_0["date"].drop_duplicates().astype(int).nlargest(1).iloc[-1])]
    df_0_2 = df_0[df_0["date"] == str(df_0["date"].drop_duplicates().astype(int).nlargest(2).iloc[-1])]
    df_2_1 = df_2[df_2["date"] == str(df_2["date"].drop_duplicates().astype(int).nsmallest(1).iloc[-1])]
    df_2_2 = df_2[df_2["date"] == str(df_2["date"].drop_duplicates().astype(int).nsmallest(2).iloc[-1])]
    df_2_3 = df_2[df_2["date"] == str(df_2["date"].drop_duplicates().astype(int).nsmallest(3).iloc[-1])]
     
    df = pd.concat([df_0_1, df_0_2, df_1, df_2_1, df_2_2, df_2_3])
    df = df.sort_values(by=["0", "date"])
    df = df[df["4"] != "0"]
    
    df.to_csv('CAR_' + str(1998 + t) + '.csv')