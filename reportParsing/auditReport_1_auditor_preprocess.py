# -*- coding: utf-8 -*-
"""
Created on 10/23/2021

@author: yoonseok

대상기간 : 1998 - 2020
적용대상 : 사업보고서 제출대상

"""

import os
import pandas as pd
import numpy as np
import re


def preprocessNumber(value):
    p = re.compile('[^ 0-9]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    return value

def preprocessAccount(value):
    p = re.compile('[^ ㄱ-ㅣ가-힣0-9]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    
    return value

def preprocessFirm(value):
    p = re.compile(".+회계법인")
    result = p.match(value)    
    try:
        value = result.group(0)
    except AttributeError:
        None
    q = re.compile("[제0-9]+호")
    result = q.match(value)    
    try:
        value = result.group(0)
    except AttributeError:
        value = value.split("감사반")
        value = value[len(value)-1]    
    return value

# Change to datafolder
os.chdir(r"C:\data2")

# 입수 재무정보 DF 변환 후 NaN 제거
df = pd.read_csv("auditReport_1_auditor.txt")
df = df[df["GAAP"].isna() == False]
start = len(df)

df["firm"] = ''
auditFirm = []

for string in df["GAAP"]:
    string = preprocessAccount(string)
    string = preprocessFirm(string)
    auditFirm.append(string)

df["auditFirm"] = auditFirm
df = df[["key", "auditFirm"]]
df.replace('', np.nan, inplace=True)
df.dropna(inplace=True)

# 이상치 제거 1 : 길이가 300을 초과하거나 5 미만인 Entry 제거
df["drop"] = [True if len(x) > 300 or len(x) < 3 else False for x in df["auditFirm"]]
df = df[df["drop"] == False]
del df["drop"]

# 매핑 자료 입력 : Unique 값에 수기 조정 매핑
dfMap = pd.read_excel(r'C:\data\financials\firmMapping.xlsx')

# 1차 매핑
df['firm'] = df['auditFirm'].map(dfMap.set_index("auditFirm")['firm'])

# 2차 매핑
dfMap = dfMap.drop_duplicates(subset=['firm'])
df['big'] = df['firm'].map(dfMap.set_index("firm")['BIG'])
df.dropna(inplace=True)

# 이상치 제거2 : 2 미만인 Entry 제거
df["drop"] = [True if len(x) < 2 else False for x in df["firm"]]
df = df[df["drop"] == False]
del df["drop"]

# 작업 검증
unique = set(df["firm"])
print(unique)
print("샘플 drop: {0}".format(start-len(df)))

# 산출치 추출
df = df[["key", "firm", "big"]]
df.to_csv("auditReport_1_auditor_preprocessed.txt")
