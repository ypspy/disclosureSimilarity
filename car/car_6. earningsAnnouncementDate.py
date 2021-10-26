# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 23:48:53 2021

@author: yoonseok
"""
import OpenDartReader
import pandas as pd
import os

# Change to datafolder
os.chdir(r"C:\data\car\\")

# 기본 테이블 입력
df = pd.read_csv("car_1_reportTypeI_list.csv", sep='\t')
del df["Unnamed: 0"]

# 백복현 등 (2012)에 따라 잠정실적/주총소집/매출액또는손익구조 변경 중 가장 빠른 날

df1 = df[df["report_nm"].str.contains("(잠정)실적", regex=False) == True]
df1 = df1[df1["report_nm"].str.contains("(자회사의 주요경영사항)", regex=False) == False]
df1 = df1[df1["report_nm"].str.contains("기재정정", regex=False) == False]

df2 = df[df["report_nm"].str.contains("주주총회소집결의", regex=False) == True]
df2 = df2[df2["report_nm"].str.contains("기재정정", regex=False) == False]

df3 = df[df["report_nm"].str.contains("매출액또는손익구조", regex=False) == True]
df3 = df3[df3["report_nm"].str.contains("(자회사의 주요경영사항)", regex=False) == False]
df3 = df3[df3["report_nm"].str.contains("기재정정", regex=False) == False]

result = pd.concat([df1, df2, df3])
result = result.sort_values(by=["stock_code", "rcept_dt"])

# 연도 코딩
result["year"] = [int(x/10000) for x in result["rcept_dt"]]

# 4월 1일 이후 공시는 1분기 혹은 이상 공시이므로 drop
result["TH"] = [x*10000+331 for x  in result["year"]] 
drop = []
for number in range(len(result)):
    if result.iloc[number,10] >= result.iloc[number,7]:
        drop.append(True)
    else:
        drop.append(False)
result["drop"] = drop
result = result[result["drop"] == True]

# key 코딩
key = []
for number in range(len(result)):
    key.append(str(result.iloc[number,2].astype(int)) + str(result.iloc[number,9]-1))
result["key"] = key

# 가장 빠른 날만 남기고 제거
result = result.drop_duplicates(subset=["key"])

# 종목코드 이익공시일 추출
result2 = result[["key", "rcept_dt"]]
result2.to_csv("car_2_earningsAccouncementDate.csv")
