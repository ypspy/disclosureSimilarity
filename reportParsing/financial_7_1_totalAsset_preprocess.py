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
    p = re.compile('[^ ㄱ-ㅣ가-힣]+')
    value = p.sub(' ', value)
    value = value.strip()  # 문서 앞뒤 공백 제거
    value = ''.join(value.split())  # Replace Multiple whitespace into one
    return value


# Change to datafolder
os.chdir(r"C:\data\financials\\")

# 입수 재무정보 DF 변환 후 NaN 제거
df = pd.read_csv("financial_8_totalAsset_separate.txt")
df = df[df["documents"].isna() == False]
start = len(df)

df["account"], df["unit"], df["value"]  = "", "", ""
account, unit, value = [], [], []

for string in df["documents"]:
    splitString = string.split("_")
    account.append(preprocessAccount(splitString[0]))
    unit.append(preprocessNumber(splitString[1]))
    value.append(preprocessNumber(splitString[2]))

df["account"], df["unit"], df["value"]  = account, unit, value

df = df[["key", "account", "unit", "value"]]
df.replace('', np.nan, inplace=True)
df.dropna(inplace=True)


# 이상치 제거 1 : 길이가 50을 초과하거나 4 미만인 Entry 제거
df["drop"] = [True if len(x) > 50 or len(x) < 4 else False for x in df["account"]]
df = df[df["drop"] == False]
del df["drop"]

# 이상치 제거 2  : set로 중복 제거하여 부적합한 계정 제거
dropList = ["제기기말", "자본총계", "이익잉여금", "기말의현금", "미지급비용",
            "및자본총계", "비지배지분", "임대보증금주", "매입외환주석", "각주상각채권",
            "비지배주주지분", "국공채창구판매", "유동화부채주석", "투자주식평가이익주석",
            "기말의현금및현금성자산", "환매권부대출채권매각주석", "첨부된재무제표에대한주석참조"]

df["drop"] = [True if x in dropList else False for x in df["account"]]
df = df[df["drop"] == False]
del df["drop"]

# 산출치 입력
df["asset"] = df["unit"].astype('int64') * df["value"].astype('int64')

# 작업 검증
unique = set(df["account"])
print(unique)
print("샘플 drop: {0}".format(start-len(df)))

#추가 Key 생성
assetKey = []
for entry in df["key"]:
    key = entry[22:]
    year = int(key[1:5])+1
    adjustedKey = ''.join(["(",str(year),key[5:]])
    
    assetKey.append(adjustedKey)
df["assetKey"] = assetKey

# 산출치 추출
df = df[["assetKey", "asset"]]
df.to_csv("financial_financial_8_totalAsset_separate_preprocessed.txt")
