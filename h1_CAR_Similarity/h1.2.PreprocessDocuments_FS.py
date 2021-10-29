# -*- coding: utf-8 -*-
"""
Created on Sat Aug  7 18:31:38 2021

@author: yoonseok

대상기간 : 1998 - 2020
적용대상 : 사업보고서 제출대상

"""

from bs4 import BeautifulSoup
import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
import re


def preprocessString(string):
    p = re.compile('[^ ㄱ-ㅣ가-힣A-Za-z]+')
    string = p.sub(' ', string)
    string = string.strip()  # 문서 앞뒤 공백 제거
    string = ' '.join(string.split())  # Replace Multiple whitespace into one
    return string

def calculateNumberRatio(tableContent):
    tableContent = ''.join(tableContent.split())
    
    p = re.compile('[^ ㄱ-ㅣ가-힣A-Za-z]+')
    string = p.sub('', tableContent)
    q = re.compile('[^ 0-9]+')
    number = q.sub('', tableContent)
        
    try:
        ratio = round(100 * len(number) / (len(string) + len(number)))
    except ZeroDivisionError:  # drop exeptional tables
        ratio = 11  
    
    return ratio


# Change to datafolder
os.chdir("C:\data\\")

# Target path list-up
pathList = []
for path in tqdm([".\A001_1999\\", ".\A001_2000\\", ".\A001_2001\\",
                  ".\A001_2002\\", ".\A001_2003\\", ".\A001_2004\\",
                  ".\A001_2005\\", ".\A001_2006\\", ".\A001_2007\\",
                  ".\A001_2008\\", ".\A001_2009\\", ".\A001_2010\\",
                  ".\A001_2011\\", ".\A001_2012\\", ".\A001_2013\\",
                  ".\A001_2014\\", ".\A001_2015\\", ".\A001_2016\\",
                  ".\A001_2017\\", ".\A001_2018\\", ".\A001_2019\\",
                  ".\A001_2020\\",]):
    
    financialStatements1 = path + "*_(첨부)재무제표*.*"  # 필요한 Keyword 입력
    pathFS1 = glob.glob(financialStatements1)
    notes = path + "*_재무제표에대한주석*.*"  # 필요한 Keyword 입력
    pathNotes = glob.glob(notes)
    
    financialStatements1C = path + "*_(첨부)연결재무제표*.*"  # 필요한 Keyword 입력
    pathFS1C = glob.glob(financialStatements1C)
    notesC = path + "*_연결재무제표에대한주석*.*"  # 필요한 Keyword 입력
    pathNotesC = glob.glob(notesC)
            
    pathList= pathList + pathFS1 + pathNotes + pathFS1C + pathNotesC

# 입수 과정에서 중복입수되어 표시된 duplicated 표시 파일 제거
pathList = [x for x in pathList if "duplicated" not in x]
print("중복입수된 문서 제거후:{}".format(len(pathList)))

# 12월 법인 분리
pathList = [x for x in pathList if ".12)" in x]
print("사업연도말이 12월이 아닌 경우 제거후:{}".format(len(pathList)))

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
# 6을 TRUE/FALSE로 조정한다. 가설 1: TRUE (최초 보고) / 가설 2 : FALSE (최종 보고)
df = df.sort_values(by=[10, 5, "con", 2, 6, "amend", 7],  
                    ascending=[True, True, True, False, 
                               True, # 가설에 따라 조정
                               True, False])  

# Remove duplicates
df["duplc"] = df.duplicated(subset=["key"], keep=False)
isTrue = df[df["duplc"] == True]
df = df.drop_duplicates(subset=["key"])
print("정정보고 등 추가 보고서 미정정 보고서/재무제표와 주석이 모두 입수된 경우 재무제표 제거 후:{}".format(len(df["key"])))

df = df.drop([0, 1, 14, "duplc"], axis=1)

df["toDrop"] = 1
for i in range(1, len(df)):
    if df.iloc[i,3] == df.iloc[i-1,3] and df.iloc[i,8] == df.iloc[i-1,8]:
        df.iloc[i, 16] = df.iloc[i-1, 16] + 1
    else:
        df.iloc[i, 16] = 1
df = df[df["toDrop"] == 1]
df = df.drop("toDrop", axis=1)

# Path out
pathListIter = df["path"].tolist()

# Strings
stringList = []
for file in tqdm(pathListIter, desc="Main Loop"):

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()
        
    soupNote = str(soup).split("주석</a>")[1]
    soup = BeautifulSoup(soupNote, 'html.parser')
    
    tables =soup.find_all("table")
        
    [table.decompose() for table in soup.find_all("table") if calculateNumberRatio(table.text) > 10]
    # Loughran and McDonald 2016
    
    string = preprocessString(soup.text)
    stringList.append(string)

df["documents"] = stringList
df.to_csv("h1.preprocessedDocumentsOut_FS.txt")
# 별도 재무제표만 입수
