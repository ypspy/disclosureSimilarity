# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 01:31:54 2021

@author: yoonseok
"""

import os
import pandas as pd
from tqdm import tqdm
from scipy.stats import mstats  # winsorize
import numpy as np

# Change to datafolder
os.chdir(r"C:\data\car\\")

# 기본 테이블 입력
df = pd.read_csv("dataframe_h1.txt")
del df["Unnamed: 0"]
df = df.dropna(subset=["8"])

# 공시일자 추출
df["date"] = [x[0:10].replace(".","") for x in df["6"]]

# 연도 입력
df["year"] = [int(x[1:5]) for x in df["5"]]

# Key 코딩
carKey = []
for number in range(len(df)):
    carKey.append(str(df.iloc[number,6].astype(int)) + str(df.iloc[number,17]))
key = []
for i in carKey:
    key.append(int(i))
df["carKey"] = key

# 이익공시일 자료 입력
df2 = pd.read_csv("car_2_earningsAccouncementDate.csv")
del df2["Unnamed: 0"]

df['dateE'] = df['carKey'].map(df2.set_index("carKey")['rcept_dt'])
df = df.dropna(subset=["dateE"])
date = []
for i in df["dateE"]:  # 이익공시 누적초과수익률은 [-1,1] 이므로 매핑 날짜를 하루 전날로 바꾼다
    if str(i)[4:8] == "0201":  # 1월 2일과 3월 2일
        i = int(str(i)[0:4] + "0131")
    else:
        i = int(i) -1
    date.append(int(i))
df["dateE"] = date

# car 코딩
car = []
for number in range(len(df)):
    car.append(str(df.iloc[number,16]) + str(df.iloc[number,6].astype(int)))
key = []
for i in car:
    key.append(int(i))
df["car"] = key

# car_e 코딩
car_e = []
for number in range(len(df)):
    car_e.append(str(df.iloc[number,19]) + str(df.iloc[number,6].astype(int)))
key = []
for i in car_e:
    key.append(int(i))
df["car_e"] = key

# CAR 작업 폴더로 변경
os.chdir("C:\data\stockinfo\car\\")  # 작업 폴더로 변경

# CAR 계산된 시트 전체 취합
year = 1999
CAR = pd.read_csv("CAR_" + str(year) +".csv", 
                 usecols=[2, 3, 5, 14, 15], 
                 dtype=str)

for year in tqdm(range(0, 21)):
    CAR2 = pd.read_csv("CAR_" + str(2000 + year) +".csv",
                       usecols=[2, 3, 5, 14, 15],
                       dtype=str)
    CAR = pd.concat([CAR, CAR2])

CAR = CAR.sort_values(by=["0", "date"])
key = []
for i in tqdm(CAR["match"]):
    try:
        key.append(int(i))
    except ValueError:
        key.append('')
CAR["match"] = key
CAR = CAR.dropna(subset=["CAR[0,2]_it"])
CAR = CAR.replace(r'^\s*$', np.nan, regex=True)
CAR = CAR.dropna(subset=["match"])
CAR = CAR.drop_duplicates(subset=["match"])

# CAR 처리 

df['car_val'] = df['car'].map(CAR.set_index("match")['CAR[0,2]_it'])
df['car_e_val'] = df['car_e'].map(CAR.set_index("match")['CAR[0,2]_it'])
df = df.dropna(subset=["car_val", "car_e_val"])

# fileLate 계산 준비

## 전기말 별도 자산총계 입력
asset_prev = pd.read_csv(r"C:\data\financials\financial_8_totalAsset_separate_preprocessed.txt")
asset_prev = asset_prev.drop_duplicates(subset=["assetKey"])

## AssetKey 생성
assetKey = []
for entry in df["key"]:
    key = entry[22:]    
    assetKey.append(key)
df["assetKey"] = assetKey

## 전기말 별도 자산총계 매핑
df['asset_py'] = df['assetKey'].map(asset_prev.set_index("assetKey")['asset'])
df = df.dropna(subset=['asset_py'])

## 2조 이상 표시
df["large"] = [1 if x >= 2000000000000 else 0 for x in df["asset_py"]]

# 유사도(SCORE^A) 산출값 DF 변환
score = pd.read_csv(r"C:\data\h1.score.count.txt")
del score["Unnamed..0"]
del score["X"]

# 총자산 DF 변환
asset = pd.read_csv(r"C:\data\financials\financial_1_totalAsset_preprocessed.txt")

# 추가 lag Asset Key 생성
assetKey = []
for entry in asset["key"]:
    key = entry[22:]
    year = int(key[1:5])
    adjustedKey = ''.join(["(",str(year),key[5:]])
    
    assetKey.append(adjustedKey)
asset["lagAssetKey"] = assetKey

assetKey = []
for entry in df["key"]:
    key = entry[22:]
    year = int(key[1:5])-1
    adjustedKey = ''.join(["(",str(year),key[5:]])
    
    assetKey.append(adjustedKey)
df["lagAssetKey"] = assetKey

lagAsset = asset.drop_duplicates(subset=["lagAssetKey"])

# 입수 감사보고서 정보 DF 변환
auditor = pd.read_csv(r"C:\data\financials\auditReport_1_auditor_preprocessed.txt")
del auditor["Unnamed: 0"]
gaap = pd.read_csv(r"C:\data\financials\auditReport_2_gaap_preprocessed.txt")
del gaap["Unnamed: 0"]

# Merge DF
result = pd.merge(df, score, how="inner", on=["key"])
result = pd.merge(result, asset[["key", "asset"]], how="inner", on=["key"])
result = pd.merge(result, auditor, how="inner", on=["key"])
result = pd.merge(result, gaap, how="inner", on=["key"])

result['lagAsset'] = result['lagAssetKey'].map(lagAsset.set_index("lagAssetKey")['asset'])

# filelate 
## 수기 매핑된 due date 테이블 입력
filelate = pd.read_csv(r"C:\data\car\filelateMap_h1.txt", sep="\t")

late = []
for entry in range(len(result)):
    if result.iloc[entry, 17] <= 2006:  # 증권거래법 시행령(대통령령)(제18757호)(20050329)
        if result.iloc[entry, 13] == "C":
            late.append(str(result.iloc[entry, 17]) + "120")
        else:
            late.append(str(result.iloc[entry, 17]) + "90")
    else:
        if result.iloc[entry, 44] == "한국채택국제회계기준":
            late.append(str(result.iloc[entry, 17]) + "90")
        elif result.iloc[entry, 13] == "C" and result.iloc[entry, 26] == 1:
            late.append(str(result.iloc[entry, 17]) + "90")
        elif result.iloc[entry, 13] == "S":
            late.append(str(result.iloc[entry, 17]) + "90")
        else:
            late.append(str(result.iloc[entry, 17]) + "120")
container = []
for val in late:
    container.append(int(val))
result["lateMap"] = container
result['dueDate'] = result['lateMap'].map(filelate.set_index("MAP")['SEP'])

filelate = []
for entry in range(len(result)):
    if int(result.iloc[entry, 47]) < int(result.iloc[entry, 16]):
        filelate.append(1)
    else:
        filelate.append(0)
result["filelate"] = filelate

# 연결 더미
consolidated =  []
for entry in range(len(result)):
    if result.iloc[entry, 13] == "C":
        consolidated.append(1)
    else:
        consolidated.append(0)
result["consolidated"] = consolidated

# 누적초과수익률 윈저라이즈 후 절대값 처리
result["car_val"] = mstats.winsorize(result["car_val"], limits=0.01)  # 절대값 처리전 윈저라이즈
container = []
for val in result["car_val"]:
    container.append(abs(float(val)))
result["car_val"] = container

# 이익공시일 누적초과수익률 윈저라이즈 후 절대값 처리
result["car_e_val"] = mstats.winsorize(result["car_e_val"], limits=0.01)  # 절대값 처리전 윈저라이즈
container = []
for val in result["car_e_val"]:
    container.append(abs(float(val)))
result["car_e_val"] = container

# 총자산 로그 처리 후 윈저라이즈
result["lnAsset"] = [np.log(x) for x in result["asset"]]
result["lnAsset"] = mstats.winsorize(result["lnAsset"], limits=0.01)
result["lnLagAsset"] = [np.log(x) for x in result["lagAsset"]]

# 추출
result["X10"] = [x.replace("-","") for x in result["10"]]
result = result[["X10", "year", "car_val", "score", "filelate", "car_e_val",
                  "lnAsset", "lnLagAsset", "modified", "gc", "consolidated"]]

os.chdir(r"C:\data\car\\")
result.to_csv("h1_variables.txt")
