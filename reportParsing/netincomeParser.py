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


def col_span_count(soup):
    try:
        result = int(soup["colspan"])
    except KeyError:
        result= 1
    return result

def row_span_count(soup):
    try:
        result = int(soup["rowspan"])
    except KeyError:
        result= 1
    return result

def FindTargetTable(soup):
    tables = soup.find_all("table")
    for i in tables:
        tds = i.find_all("td")
        if len(tds) > 20:  # 시간 파트가 약 80정도 된다. 비교 표시 없는 경우 td가 50도 안된다. 첫번째 나오는 20 초과 table 선택
            break
    return i

def MatrixGenerator(table):
    table_row = table.find_all("tr")

    columnCount = 0
    for i in table_row:
        columnNumber = 0
        for j in i.find_all(["th", "td"]):
            try:
                columnNumber += int(j["colspan"])
            except KeyError:
                columnNumber += 1
            if columnNumber > columnCount:
                columnCount = columnNumber        
    rowCount = len(table_row)
    matrix = [['#' for x in range(columnCount)] for y in range(rowCount)] 
    for i in range(len(table_row)):
        locator = [i for i, x in enumerate(matrix[i]) if x=='#']  # https://stackoverflow.com/questions/9542738/python-find-in-list
        column, colSpan = 0, 0
        for j in table_row[i].find_all(["th", "td"]):
            rowSpanCount = row_span_count(j)
            colSpanCount = col_span_count(j)

            for k in range(rowSpanCount):
                for l in range(colSpanCount):
                    row = i + k
                    column = locator[l+colSpan]
                    matrix[row][column] = j.text.strip()
            colSpan += col_span_count(j)
    return matrix


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
    financialStatements2 = path + "*_(첨부)연결재무제표*.*"  # 필요한 Keyword 입력
    pathFS2 = glob.glob(financialStatements2)
    financialStatements3 = path + "*_재무제표_*.*"  # 필요한 Keyword 입력
    pathFS3 = glob.glob(financialStatements3)
    financialStatements4 = path + "*_연결재무제표_*.*"  # 필요한 Keyword 입력
    pathFS4 = glob.glob(financialStatements4)
            
    pathList= pathList + pathFS1 + pathFS2 + pathFS3 + pathFS4 

# 입수 과정에서 중복입수되어 표시된 duplicated 표시 파일 제거
pathList = [x for x in pathList if "duplicated" not in x]

# 12월 법인 분리
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
result = []
for file in tqdm(pathListIter, desc="Main Loop"):

    html = open(file, "r", encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    html.close()

    soup = str(soup).split("주석</A>")[0]
    soup = soup.replace("\n", '')
    soup = BeautifulSoup(soup, "lxml")
    
    # 단위 추출
    for td in soup.find_all(["p","td"]):
        if ''.join(td.text.split()).find("단위") > 0:
            unit = ''.join(td.text.split())
            if unit.find(":원") > 0:
                unit = '1'
            elif unit.find(":천원") > 0:
                unit = '1000'
            elif unit.find(":백만원") > 0:
                unit = '1000000'
            else:
                unit = "NA"           
            break

    # IS 찾기
    
    for table in soup.find_all("table"):
        matchesNeg = ["미처분", "미처리", "이익잉여금", "결손"]
        i = "".join(table.text.split())
        if "당기순" in i and all(x not in i for x in matchesNeg):
            break
        table = BeautifulSoup("<table></table>", features="lxml").table
    
    matrix = MatrixGenerator(table)
        
    # Net Income Parsing

    resultString = ''
    isLine = ''
    
    if len(matrix) > 0:  # IS가 있을 때
        
        exitKey = False
        for i in matrix:
           for j in i:

               matchesNeg = ["계속", "중단", "귀속", "미처분", "미처리", "처분전",
                             "지배", "비지배", "관계", "공동", "차감전", "이익잉여금",
                             "결손", "剩餘金"]
               matchesPos = ["당기순", "當期純"]
               j = "".join(j.split())
               
               if any(x in j for x in matchesPos) and all(x not in j for x in matchesNeg):
                                        
                    if len(i) == 2:  # 오리온 (2018.12)
                        isLine = [i[0], unit, i[1].replace("=", "")]        
                    elif len(i) % 2 == 1:  # 주석 Column이 없을 때
                        if i[1]:
                            isLine = [i[0], unit, i[1].replace("=", "")]
                        elif i[2]:
                            isLine = [i[0], unit, i[2].replace("=", "")]
                    else:  # 주석 Column이 있을 때
                        if i[2]:
                            isLine = [i[0], unit, i[2].replace("=", "")]
                        elif i[3]:
                            isLine = [i[0], unit, i[3].replace("=", "")]
        
                    resultString = "_".join(isLine)
                    exitKey = True                    
                    break
            
           if exitKey == True:
               break

    elif len(matrix) == 0:  # BS가 없을 때
        resultString = ""
    
    result.append(resultString)

df["netIncome"] = result
df.to_csv("netIncome_output.txt")
