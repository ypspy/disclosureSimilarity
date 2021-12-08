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
os.chdir(r"C:\data2")

# 입수 재무정보 DF 변환 후 NaN 제거
df = pd.read_csv("financial_7_investingCashFlow.txt")
df = df[df["account"].isna() == False]
start = len(df)

df["accounts"], df["unit"], df["value"], df["valueSigned"]  = "", "", "", ""
account, unit, value, valueSigned = [], [], [], []

for string in df["account"]:
    splitString = string.split("_")
    
    acc = preprocessAccount(splitString[0])
    account.append(acc)
    unit.append(preprocessNumber(splitString[1]))
    
    x = ''
    x = preprocessSignedNumber1(splitString[2])
    
    if preprocessSignedNumber2(x):
        valueSign = -1
    else:
        valueSign = 1
    value.append(preprocessNumber(x))
    valueSigned.append(valueSign)

df["accounts"], df["unit"], df["value"], df["valueSigned"]  = account, unit, value, valueSigned

df = df[["key", "accounts", "unit", "value", "valueSigned"]]
df.replace('', np.nan, inplace=True)
df.dropna(inplace=True)

# 이상치 제거 1 길이가 20을 초과한 Entry 제거
df["drop"] = [True if len(x) > 20 else False for x in df["accounts"]]
df = df[df["drop"] == False]
del df["drop"]

# 산출값 Integer로 변경
df["value"] = [int(x) for x in df["value"]]

# 산출치 입력
df["investingCF"] = df["unit"].astype('int') * df["value"] * df["valueSigned"]

# 작업 검증 (순이익은 사용하지 않음)
unique = set(df["accounts"])
print(unique)
print("샘플 drop: {0}".format(start-len(df)))

# # 산출치 추출
df = df[["key", "investingCF"]]
df.to_csv("financial_7_investingCashFlow_preprocessed.txt")
