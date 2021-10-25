# -*- coding: utf-8 -*-
"""
Created on 10/23/2021

@author: yoonseok

대상기간 : 1998 - 2020
적용대상 : 사업보고서 제출대상

"""

import os
import pandas as pd
from tqdm import tqdm
from scipy.stats import mstats  # winsorize


# Change to datafolder
os.chdir(r"C:\data\financials\\")

# 기본 테이블 입력
df = pd.read_csv("dataframe.txt")
del df["Unnamed: 0"]

df["toDrop"] = 1
for i in range(1, len(df)):
    if df.iloc[i,3] == df.iloc[i-1,3] and df.iloc[i,8] == df.iloc[i-1,8]:
        df.iloc[i, 16] = df.iloc[i-1, 16] + 1
    else:
        df.iloc[i, 16] = 1
df = df[df["toDrop"] == 1]
df = df.drop("toDrop", axis=1)

# 입수 재무정보 DF 변환
df1 = pd.read_csv("financial_1_totalAsset_preprocessed.txt")
df2 = pd.read_csv("financial_2_totalEquity_preprocessed.txt")
df3 = pd.read_csv("financial_3_netIncome_preprocessed.txt")
df4 = pd.read_csv("financial_4_currentAsset_preprocessed.txt")
df5 = pd.read_csv("financial_5_currentLiability_preprocessed.txt")
df6 = pd.read_csv("financial_6_operatingCashFlow_preprocessed.txt")
df7 = pd.read_csv("financial_7_investingCashFlow_preprocessed.txt")

# 입수 감사보고서 정보 DF 변환
df8 = pd.read_csv("auditReport_1_auditor_preprocessed.txt")
df9 = pd.read_csv("auditReport_2_gaap_preprocessed.txt")

# 유사도(SCORE^B) 산출값 DF 변환
df10 = pd.read_csv(r"C:\data\h2.score.txt")

# index column 일괄 제거
for table in [df1, df2, df3, df4, df5, df6, df7, df8, df9]:
    del table["Unnamed: 0"]
del df10["Unnamed..0"]
del df10["X"]

# Key로 Merge
result = pd.merge(df1, df2, how="inner", on=["key"])
for table in [df3, df4, df5, df6, df7, df8, 
              df9[["key", "ifrs", "modified", "gc"]], 
              df10[["key", "length", "score"]]]:
    result = pd.merge(result, table, how="inner", on=["key"]) 

result = pd.merge(result, df, how="inner", on=["key"]) 

# 법인등록번호 누락 Entry 제거
result = result[result["10"].isna() == False]

# 동일 기업 식별자 추가
FIRM = [False]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1, 24] == result.iloc[entry, 24] :
        FIRM.append(True)
    else:
        FIRM.append(False)
result["FIRM"] = FIRM

# 연속 감사 식별자 추가
cons = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1, 31]:
        year = int(result.iloc[entry+1, 19][1:5]) - int(result.iloc[entry, 19][1:5])
        cons.append(year)
    else:
        cons.append(0)
result["cons"] = cons

# 총부채 입력
liability = []
for entry in tqdm(range(len(result))):
    if result.iloc[entry, 3]:
        liability.append(result.iloc[entry, 1]-result.iloc[entry, 2])
    else:
        liability.append(result.iloc[entry, 2])
result["liability"] = liability
del result["credit"]
del result["equity"]

# ROA 계산
roa = []
for entry in tqdm(range(len(result))):
    roa.append(result.iloc[entry,2]/result.iloc[entry,1])
result["roa"] = roa
result["roa"] = result["roa"].round(4)

# 유동비율 계산
result = result[result["currentLiability"] != 0]  # 유동부채 0 Entry 제거
current = []
for entry in tqdm(range(len(result))):
    current.append(result.iloc[entry,3]/result.iloc[entry,4])
result["current"] = current
result["current"] = result["current"].round(4)

# 유동부채비중 계산
debtdue = []
for entry in tqdm(range(len(result))):
    debtdue.append(result.iloc[entry,4]/result.iloc[entry,1])
result["debtdue"] = debtdue
result["debtdue"] = result["debtdue"].round(4)

# 부채비중 계산
leverage = []
for entry in tqdm(range(len(result))):
    leverage.append(result.iloc[entry,31]/result.iloc[entry,1])
result["leverage"] = leverage
result["leverage"] = result["leverage"].round(4)

# 잉여현금흐름 계산
fcf = []
for entry in tqdm(range(len(result))):
    fcf.append((result.iloc[entry,5]+result.iloc[entry,6])/result.iloc[entry,1])
result["fcf"] = fcf
result["fcf"] = result["fcf"].round(4)

# 자산 변동율 계산 후 30% 초과 변동 더미 표시
assetRatio, merger, split = [0], [0], [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        ratio = result.iloc[entry+1, 1] / result.iloc[entry, 1]
        assetRatio.append(ratio)
        if ratio >= 1.3:
            merger.append(1)
        else:
            merger.append(0)
        if ratio <= 0.7:
            split.append(1)
        else:
            split.append(0)
    else:
        assetRatio.append(0)
        merger.append(0)
        split.append(0)
        
result["assetRatio"] = assetRatio
result["assetRatio"] = result["assetRatio"].round(4)
result["merger"] = merger
result["split"] = split

# ROA 변동 절대값
dROA = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        diff = result.iloc[entry+1, 32] - result.iloc[entry, 32]
        dROA.append(diff)
    else:
        dROA.append(0)
result["dROA"] = dROA
result["dROA"] = result["dROA"].round(4)

result["dROA"] = mstats.winsorize(result["dROA"], limits=0.01)  # 절대값 처리전 윈저라이즈
result["dROA"] = result["dROA"].abs()

# CURRENT 변동 절대값
dCURRENT = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        diff = result.iloc[entry+1, 33] - result.iloc[entry, 33]
        dCURRENT.append(diff)
    else:
        dCURRENT.append(0)
        
result["dCURRENT"] = dCURRENT
result["dCURRENT"] = result["dCURRENT"].round(4)

result["dCURRENT"] = mstats.winsorize(result["dCURRENT"], limits=0.01)  # 절대값 처리전 윈저라이즈
result["dCURRENT"] = result["dCURRENT"].abs()


# DEBTDUE 변동 절대값
dDEBTDUE = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        diff = result.iloc[entry+1, 34] - result.iloc[entry, 34]
        dDEBTDUE.append(diff)
    else:
        dDEBTDUE.append(0)
        
result["dDEBTDUE"] = dDEBTDUE
result["dDEBTDUE"] = result["dDEBTDUE"].round(4)

result["dDEBTDUE"] = mstats.winsorize(result["dDEBTDUE"], limits=0.01)  # 절대값 처리전 윈저라이즈
result["dDEBTDUE"] = result["dDEBTDUE"].abs()


# LEVERAGE 변동 절대값
dLEVERAGE = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        diff = result.iloc[entry+1, 35] - result.iloc[entry, 35]
        dLEVERAGE.append(diff)
    else:
        dLEVERAGE.append(0)
        
result["dLEVERAGE"] = dLEVERAGE
result["dLEVERAGE"] = result["dLEVERAGE"].round(4)

result["dLEVERAGE"] = mstats.winsorize(result["dLEVERAGE"], limits=0.01)  # 절대값 처리전 윈저라이즈
result["dLEVERAGE"] = result["dLEVERAGE"].abs()

# FCF 변동 절대값
dFCF = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        diff = result.iloc[entry+1, 36] - result.iloc[entry, 36]
        dFCF.append(diff)
    else:
        dFCF.append(0)
        
result["dFCF"] = dFCF
result["dFCF"] = result["dFCF"].round(4)

result["dFCF"] = mstats.winsorize(result["dFCF"], limits=0.01)  # 절대값 처리전 윈저라이즈
result["dFCF"] = result["dFCF"].abs()

# 연도 입력
year, post = [], []
for entry in tqdm(range(len(result))):
    ye = int(result.iloc[entry, 17][1:5])
    year.append(ye)
    if ye > 2010:
        post.append(1)
    else:
        post.append(0)    
result["year"] = year
result["post"] = post

# gaap 변수 입력 → 앞에서 넣으면 숫자가 다 바뀐다. 그래서 여기서 머지
result = pd.merge(result, df9[["key", "gaap"]], how="inner", on=["key"])

# adopt IFRS/일반기업 최초채택
adopt = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        if result.iloc[entry+1, 47] != result.iloc[entry, 47]:
            adopt.append(1)
        else:
            adopt.append(0)
    else:
        adopt.append(0)
result["adopt"] = adopt

# FIRST 감사인 변경
first = [0]
for entry in tqdm(range(len(result)-1)):
    if result.iloc[entry+1,29] == True and result.iloc[entry+1,30] == 1:
        if result.iloc[entry+1, 7] != result.iloc[entry, 7]:
            first.append(1)
        else:
            first.append(0)
    else:
        first.append(0)
result["first"] = first

# 전기 비교 불가 Entry 제거
result2 = result[result["FIRM"] == True]
result2 = result2[result["cons"] == 1]

# 추출
result2["10"] = [x.replace("-","") for x in result2["10"]]
result2 = result2[["10", "year", "score", "post", "ifrs", "adopt",
                   "dROA", "dCURRENT", "dDEBTDUE", "dLEVERAGE", "dFCF",
                   "merger", "split", "big", "first"]]

result2.to_csv("h2_variables.txt")
