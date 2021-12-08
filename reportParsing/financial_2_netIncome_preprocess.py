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
df = pd.read_csv("financial_3_netIncome.txt")
df = df[df["netIncome"].isna() == False]
start = len(df)

df["account"], df["unit"], df["value"], df["valueSigned"]  = "", "", "", ""
account, unit, value, valueSigned = [], [], [], []

for string in df["netIncome"]:
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

# 이상치 제거 1 : 단위 정보에 이상 정보
dropList = ["355421186435918133873554211864"]

df["drop"] = [True if x in dropList else False for x in df["unit"]]
df = df[df["drop"] == False]
del df["drop"]

# 이상치 제거 2 : 대손준비금 조정이익 표시 제거
df["drop"] = [True if "조정이익" in x else False for x in df["account"]]
df = df[df["drop"] == False]
del df["drop"]

# 이상치 제거 3  : set로 중복 제거하여 부적합한 계정 제거
dropList = ["기타사항", "당기순공사원가", "당기순이익총포괄이익",
            "법인세등주석당기순이익주당경상익주석당기원전기원주당순이익당기원전기원",
            "보고부문당기순이익", "보통주당기순손익주", "보통주당기순이익",
            "보통주당기순이익손실", "조정후당기순이익", "종속법인의당기순손익에대한지분감소",
            "지분법적용대상인종속기업의당기순손익에대한지분",
            "지분법적용투자자산의당기순손익에대한지분증가",
            "지분법적용투자자산의당기순손익에대한지분증감",
            "지분법피투자기업의당기순손익에대한지분증가",
            "영업수익투자수익투자주식처분이익주석투자사채수입이자약정투자수익투자조합수익조합관리보수주석운용수익수입이자유가증권이자유가증권처분이익투자유가증권처분이익영업비용투자및금융비용지급이자유가증권처분손실유가증권매매수수료대손상각일반관리비인건비경비영업이익영업외수익수입이자외환차익외화환산이익주석유형자산처분이익잡이익주석영업외비용투자주식감액손실주석투자사채감액손실주석약정투자감액손실주석조합출자금감액손실주석외화환산손실주석법인세추납액경상이익특별손실기타손실주석법인세비용전순이익법인세비용주석당기순이익주당경상이익원주당순이익원주석",
            "당기순손실주주당경상손실당기원전기원주당순손실당기원전기원"]

df["drop"] = [True if x in dropList else False for x in df["account"]]
df = df[df["drop"] == False]
del df["drop"]

# 산출치 입력
df["netIncome"] = df["unit"].astype('int') * df["value"] * df["valueSigned"]

# # 작업 검증 (순이익은 사용하지 않음)
# # unique = set(df["account"])
# # print(unique)
print("샘플 drop: {0}".format(start-len(df)))

# # 산출치 추출
df = df[["key", "netIncome"]]
df.to_csv("financial_3_netIncome_preprocessed.txt")
