# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 11:42:30 2021

@author: yoonseok
"""

import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm


# Change to datafolder
os.chdir("C:\data2\\")

df = pd.read_csv("voluntary_1_auditReport_2_gaap.txt")

# Target path list-up
pathList = df["path"]

# 입수 과정에서 중복입수되어 표시된 duplicated 표시 파일 제거
print("전체 입수문서:{}".format(len(pathList)))
pathList = [x for x in pathList if "duplicated" not in x]
print("중복입수된 문서 제거후:{}".format(len(pathList)))

# 12월 법인 분리
pathList = [x for x in pathList if ".12)" in x]
print("사업연도말이 12월이 아닌 경우 제거후:{}".format(len(pathList)))

# 입수 data의 PathList 정보로 Tabulate
PathListDf = pd.DataFrame(pathList)
df = pd.DataFrame([x.split("_") for x in pathList])

# Generate Unique Key
df["path"] = PathListDf[0]
df["con"] = df[6].str.contains("연결")
df['con'] = np.where(df['con']==True, "C", "S")
df['amend'] = df[6].str.contains("정정")
df['amend'] = np.where(df['amend']==True, "A", "B")
df["key"] = df[2] + df[6].str.slice(stop=10) + df["con"] \
          + df["amend"] + df[5] + df[8] + df[10]

# sort by Entity
# 6을 TRUE/FALSE로 조정한다. 가설 1: TRUE (최초 보고) / 가설 2 : FALSE (최종 보고)
df = df.sort_values(by=[10, 5, "con", 2, 6, "amend", 7],  
                    ascending=[True, True, True, False, 
                               False, # 가설에 따라 조정
                               True, False])  

# Remove duplicates
df["duplc"] = df.duplicated(subset=["key"], keep=False)
isTrue = df[df["duplc"] == True]
df = df.drop_duplicates(subset=["key"])
print("정정보고 등 추가 보고서 미정정 보고서/재무제표와 주석이 모두 입수된 경우 재무제표 제거 후:{}".format(len(df["key"])))

df = df.drop([0, 1, 14, "duplc"], axis=1)

df["toDrop"] = 1
for i in range(1, len(df)):
    if df.iloc[i,3] == df.iloc[i-1,3] and df.iloc[i,8] == df.iloc[i-1,8]:
        df.iloc[i, 16] = df.iloc[i-1, 16] + 1
    else:
        df.iloc[i, 16] = 1
df = df[df["toDrop"] == 1]
df = df.drop("toDrop", axis=1)
print("최종 접수 연결보고서 (별도, 정정전 보고서 제거):{}".format(len(df["key"])))

df_ind = pd.read_excel("industry.xlsx", dtype={'KSIC': str}, sheet_name='data')
df = df.rename(columns={11: "INDUSTRY"})
df2 = pd.merge(df, df_ind, on = "INDUSTRY", how ='left')
df2 = df2[df2["FIN"] == 0]

stock = []
for i in range(len(df2)):
    if len(df2.iloc[i,6]) == 0:
        stock.append(True)
    else:
        stock.append(False)
df2["stock"] = stock
df2 = df2[df2["stock"] == True]

# df2.to_csv("voluntary_2_pathList.txt")
