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
    path1 = path + "* 감사보고서_감*.*"  # 필요한 Keyword 입력
    pathSep = glob.glob(path1)
    path2 = path + "* 연결감사보고서_감*.*"  # 필요한 Keyword 입력
    pathCon = glob.glob(path2)
    
    pathList = pathList + pathSep + pathCon

# 3. 입수 과정에서 중복입수되어 표시된 duplicated 표시 파일 제거
pathList = [x for x in pathList if "duplicated" not in x]

# 4. 12월말만 분리
pathList = [x for x in pathList if ".12)" in x]

# 입수 data의 PathList 정보로 Tabulate
PathListDf = pd.DataFrame(pathList)
df = pd.DataFrame([x.split("_") for x in pathList])

# Generate Unique Key
df["path"] = PathListDf[0]
df["con"] = df[6].str.contains("연결")
df['con'] = np.where(df['con']==True, "C", "S")
df['amend'] = df[6].str.contains("정정")
df['amend'] = np.where(df['amend']==True, "A", "B")
df["key"] = df[2] + df[6].str.slice(stop=10) + df["con"] \
          + df["amend"] + df[5] + df[8] + df[10]

# sort by Entity
df = df.sort_values(by=[10, 5, "con", 2, 6, "amend"],
                    ascending=[True, True, True, False, False, True])

# Remove duplicates
df["duplc"] = df.duplicated(subset=["key"], keep=False)
isTrue = df[df["duplc"] == True]
df = df.drop_duplicates(subset=["key"])

df = df.drop([0, 1, 14, "duplc"], axis=1)

# Path out
pathListOut = df["path"].tolist()

result = []

for file in tqdm(pathListOut, desc="Main Loop"):

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()
    
    firmName = ''
    
    for i in soup.find_all('p'):
        pText = ''.join(i.text.split())
        if "회계법인" in pText:
            firmName = pText
        if "감사반" in pText:
            firmName = pText
       
    for i in soup.find_all('td'):
        pText = ''.join(i.text.split())
        if "회계법인" in pText:
            firmName = pText
        if "감사반" in pText:
            firmName = pText
    
    if firmName == '':
        firmName = "누락"
    
    result.append(firmName)

df["GAAP"] = result
df = df[["key", 10, 5, "GAAP"]]

os.chdir("C:\data\\financials\\")
df.to_csv("auditReport_1_auditor.txt")
