# -*- coding: utf-8 -*-
"""
Created on 10/23/2021

@author: yoonseok

대상기간 : 1998 - 2020
적용대상 : 사업보고서 제출대상

"""

import os
import pandas as pd
import re


def preprocessAccount(value):
    p = re.compile('[^ ㄱ-ㅣ가-힣0-9]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    
    return value


# Change to datafolder
os.chdir(r"C:\data\financials\\")

# 입수 재무정보 DF 변환 후 NaN 제거
df = pd.read_csv("auditReport_2_gaap.txt")
df = df[df["GAAP"].isna() == False]
start = len(df)

df["gaap"], df["opinion"] = "", ""
gaap, opinion = [], []

for string in df["GAAP"]:
    splitString = string.split("\t")
    gaap.append(preprocessAccount(splitString[0]))
    opinion.append(preprocessAccount(splitString[1]))
df["gaap"], df["opinion"] = gaap, opinion 

# IFRS 더미 변수 입력
df["ifrs"] = [1 if x == "한국채택국제회계기준" else 0 for x in df["gaap"]]

# Modified 더미 변수 입력
df["modified"] = [1 if x != "적정" and x != "적정계속기업" else 0 for x in df["opinion"]]

# Going Concern 더미 변수 입력
df["gc"] = [1 if x == "적정계속기업" else 0 for x in df["opinion"]]

# 작업 검증
unique = set(df["gaap"])
print(unique)
print("샘플 drop: {0}".format(start-len(df)))

unique = set(df["opinion"])
print(unique)
print("샘플 drop: {0}".format(start-len(df)))

# 산출치 추출
df = df[["key", "ifrs", "modified", "gc"]]
df.to_csv("auditReport_2_gaap_preprocessed.txt")
