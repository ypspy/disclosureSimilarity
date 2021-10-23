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

def preprocessSignedNumber1(value):
    p = re.compile('[^ 0-9-\(\)△]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    return value

def preprocessSignedNumber2(value):
    p = re.compile('[0-9]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    return value

def preprocessAccount(value):
    p = re.compile('[^ ㄱ-ㅣ가-힣]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    return value


# Change to datafolder
os.chdir(r"C:\data\financials\\")

# 입수 재무정보 DF 변환 후 NaN 제거
df = pd.read_csv("financial_2_totalEquity.txt")
df = df[df["documents"].isna() == False]
start = len(df)

df["account"], df["unit"], df["value"], df["valueSigned"]  = "", "", "", ""
account, unit, value, valueSigned = [], [], [], []

for string in df["documents"]:
    splitString = string.split("_")
    
    acc = preprocessAccount(splitString[0])
    account.append(acc)
    unit.append(preprocessNumber(splitString[1]))
    
    x = ''
    x = preprocessSignedNumber1(splitString[2])
    loss = ''
    if "당기순손실" in acc:
        loss = True
    else:
        loss = False
    
    if preprocessSignedNumber2(x) or loss:
        valueSign = -1
    else:
        valueSign = 1
    value.append(preprocessNumber(x))
    valueSigned.append(valueSign)

df["account"], df["unit"], df["value"], df["valueSigned"]  = account, unit, value, valueSigned

df = df[["key", "account", "unit", "value", "valueSigned"]]
df.replace('', np.nan, inplace=True)
df.dropna(inplace=True)

df["value"] = [int(x) for x in df["value"]]


# 이상치 제거 1 : 길이가 50을 초과하거나 4 미만인 Entry 제거
df["drop"] = [True if len(x) > 5 or len(x) < 2 else False for x in df["account"]]
df = df[df["drop"] == False]
del df["drop"]

# 이상치 제거 2  : set로 중복 제거하여 부적합한 계정 제거
dropList = ["구분", "과목", "예수금", "기타자본", "사채주석",
            "연결조정대", "이익잉여금", "기초의현금", "비지배지분",
            "자산총계"]

df["drop"] = [True if x in dropList else False for x in df["account"]]
df = df[df["drop"] == False]
del df["drop"]

# # 산출치 입력
df["credit"] = df["unit"].astype('int64') * df["value"] * df["valueSigned"]
equityList = ['자본계', '지본총계', '자본총계', '자본합계', '자본소계', '자본총액',
              '자본', '자본총계주']
df["equity"] = [True if x in equityList else False for x in df["account"]]

# # 작업 검증
unique = set(df["account"])
print(unique)
print("샘플 drop: {0}".format(start-len(df)))

# # 산출치 추출
df = df[["key", "credit", "equity"]]
df.to_csv("financial_2_totalEquity_preprocessed.txt")
