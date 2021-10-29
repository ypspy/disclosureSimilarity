# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 23:48:53 2021

@author: yoonseok
"""
import pandas as pd
import os

# Change to datafolder
os.chdir(r"C:\data\car\\")

# Report I 입력
dfA = pd.read_csv("car_1_reportTypeI_list.csv")
del dfA["Unnamed: 0"]

df1 = dfA[dfA["report_nm"].str.contains("(잠정)실적", regex=False) == True]
df1 = df1[df1["report_nm"].str.contains("(자회사의 주요경영사항)", regex=False) == False]

df2 = dfA[dfA["report_nm"].str.contains("매출액또는손익구조", regex=False) == True]
df2 = df2[df2["report_nm"].str.contains("(자회사의 주요경영사항)", regex=False) == False]

dfA = pd.concat([df1, df2])
dfA = dfA.sort_values(by=["stock_code", "rcept_dt"])

# 연도 코딩
dfA["year"] = [int(x/10000) for x in dfA["rcept_dt"]]

# 4월 1일 이후 공시는 1분기 혹은 이상 공시이므로 drop
dfA["TH"] = [x*10000+331 for x  in dfA["year"]] 
drop = []
for number in range(len(dfA)):
    if dfA.iloc[number,10] >= dfA.iloc[number,7]:
        drop.append(True)
    else:
        drop.append(False)
dfA["drop"] = drop

dfA = dfA[dfA["drop"] == True]
del dfA["drop"]

key = []
for entry in range(len(dfA)):
    key.append(str(dfA.iloc[entry,2])+str(dfA.iloc[entry,9]))
dfA["key"] = key

# Report E 입력
dfB = pd.read_csv("car_1_reportTypeE_list.csv")
del dfB["Unnamed: 0"]

df1 = dfB[dfB["report_nm"].str.contains("경영참고사항", regex=False) == True]
df2 = dfB[dfB["report_nm"].str.contains("주주총회소집공고", regex=False) == True]

dfB = pd.concat([df1, df2])
dfB = dfB.sort_values(by=["stock_code", "rcept_dt"])

# 연도 코딩
dfB["year"] = [int(x/10000) for x in dfB["rcept_dt"]]

# 4월 1일 이후 공시는 1분기 혹은 이상 공시이므로 drop
dfB["TH"] = [x*10000+331 for x  in dfB["year"]] 
drop = []
for number in range(len(dfB)):
    if dfB.iloc[number,10] >= dfB.iloc[number,7]:
        drop.append(True)
    else:
        drop.append(False)
dfB["drop"] = drop

dfB = dfB[dfB["drop"] == True]
del dfB["drop"]

key = []
for entry in range(len(dfB)):
    key.append(str(dfB.iloc[entry,2])+str(dfB.iloc[entry,9]))
dfB["key"] = key

dfB = dfB.sort_values(by=["key"])

dfB = dfB.drop_duplicates(subset=["key"])

# 백복현 등 (2012)에 따라 잠정실적/주총소집/매출액또는손익구조 변경 중 가장 빠른 날

result = pd.concat([dfA, dfB])
result = result.sort_values(by=["key", "rcept_dt"])
result = result.drop_duplicates(subset=["key"])

# key 코딩
key = []
for number in range(len(result)):
    key.append(str(result.iloc[number,2].astype(int)) + str(result.iloc[number,9]-1))
result["carKey"] = key

# 종목코드 이익공시일 추출
result2 = result[["carKey", "year", "rcept_dt"]]
result2.to_csv("car_2_earningsAccouncementDate.csv")
