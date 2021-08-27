# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:19:08 2020

@author: user
"""

from bs4 import BeautifulSoup
import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm

# 1. 작업 폴더로 변경
os.chdir("C:\data\\")  # 작업 폴더로 변경

# 2. 타겟 폴더에 있는 필요 문서 경로 리스트업
pathList = []
for path in tqdm([".\A001_1999\\", ".\A001_2000\\", ".\A001_2001\\",
                  ".\A001_2002\\", ".\A001_2003\\", ".\A001_2004\\",
                  ".\A001_2005\\", ".\A001_2006\\", ".\A001_2007\\",
                  ".\A001_2008\\", ".\A001_2009\\", ".\A001_2010\\",
                  ".\A001_2011\\", ".\A001_2012\\", ".\A001_2013\\",
                  ".\A001_2014\\", ".\A001_2015\\", ".\A001_2016\\",
                  ".\A001_2017\\", ".\A001_2018\\", ".\A001_2019\\",
                  ".\A001_2020\\",
                  ]):
    path = path + "*감사인의감사보고서*.*"  # 필요한 Keyword 입력
    pathInProcess = glob.glob(path)
    pathList = pathList + pathInProcess

# 3. 입수 과정에서 중복입수되어 표시된 duplicated 표시 파일 제거
pathList = [x for x in pathList if "duplicated" not in x]

# 4. 12월말만 분리
pathList = [x for x in pathList if ".12)" in x]

# 5. Preprocess
PathListDf = pd.DataFrame(pathList)
df = pd.DataFrame([x.split("_") for x in pathList])
df["path"] = PathListDf[0]
df["con"] = df[6].str.contains("연결")
df['con'] = np.where(df['con']==True, "C", "S")
df['amend'] = df[6].str.contains("정정")
df['amend'] = np.where(df['amend']==True, "A", "B")
df["key"] = df[2] + df[6].str.slice(stop=10) + df["con"] + df["amend"] \
    + df[5] + df[8] + df[10]
# key = 접수일 + 보고서 제출일(DRT 인증일) + 연결(C/S) + 정정(A/B) + 보고기간종료월 + 종목코드 + 법인등록번호

df["duplc"] = df.duplicated(subset=["key"], keep=False)
isTrue = df[df["duplc"] == True]
df = df.drop_duplicates(subset=["key"])

df = df.drop([0, 1, 14, "duplc"], axis=1)

df = df.sort_values(by=[10, 5, "con", 2, 6, "amend"],
                    ascending=[True, True, True, False, False, True])

df["toDrop"] = 1
for i in range(1, len(df)):
    if df.iloc[i,3] == df.iloc[i-1,3] and df.iloc[i,8] == df.iloc[i-1,8]:
        df.iloc[i, 16] = df.iloc[i-1, 16] + 1
    else:
        df.iloc[i, 16] = 1
df = df[df["toDrop"] == 1]
df = df.drop("toDrop", axis=1)

# Path out
pathListOut = df["path"].tolist()

result = []
count = 0

KGAAP = ["일반기업회계기준에따라", "일반회계기준에따라", "一般企業會計基準에따라", "일반기업회계처리기준에따라",
         "'일반기업회계기준'에 따라"]
KIFRS = ["한국채택국제회계기준에따라", "한국채택회계기준"]

GAAP = [KGAAP, KIFRS]
tag = ["일반기업회계기준", "한국채택국제회계기준"]


# disclaimer of opinion
keyWord1 = ['의견거절근거', '의견을표명하지않', '감사의견을표명하지아니합니다',
            '의견을표명하지아니', '의견을표명할수없']
# qualified 
keyWord2 = ['한정의견근거', '한정의견근거단락에기술된사항이미치는영향을제외',
            '영향을제외하고는', '누락을제외하고는']
# adverse
keyWord3 = ['부적정의견근거', '부적정의견근거단락에서기술된사항의유의성',
            '적정하게표시하고있지아니']

keyWord = [keyWord1, keyWord2, keyWord3]
opinion = ["의견거절", "한정", "부적정"]


for file in tqdm(pathListOut, desc="Main Loop"):

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()
    
    content = ''.join(soup.text.split())
    
    num = 0

    accountingStandard = "기타" 
    for i in GAAP:
        for j in i:
            if j in content:            
                accountingStandard = tag[num]
                break
        num += 1
    
    num = 0

    auditOpinion = "적정" 
    for i in keyWord:
        for j in i:
            if j in content:        
                auditOpinion = opinion[num] 
                break
        num += 1
    returnText = accountingStandard + "\t" + auditOpinion 
        
    result.append(returnText)

df["GAAP"] = result
df = df[["key", 10, 5, "GAAP"]]

df.to_csv("gaap_output.csv", sep="\t")
