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
os.chdir("C:\data2\\")

# Target path list-up
pathList = []
for path in tqdm([".\F001_2009\\", ".\F001_2010\\",
                  ".\F001_2011\\", ".\F001_2012\\", ".\F001_2013\\",
                  ".\F001_2014\\", ".\F001_2015\\", ".\F001_2016\\",
                  ".\F001_2017\\", ".\F001_2018\\", ".\F001_2019\\",
                  ".\F001_2020\\",
                  ".\F002_2009\\", ".\F002_2010\\",
                  ".\F002_2011\\", ".\F002_2012\\", ".\F002_2013\\",
                  ".\F002_2014\\", ".\F002_2015\\", ".\F002_2016\\",
                  ".\F002_2017\\", ".\F002_2018\\", ".\F002_2019\\",
                  ".\F002_2020\\",
                  ]):
    
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

# key에 포함할 내용만 추가
df2 = pd.read_csv("voluntary_2_pathList.txt")

df = pd.merge(df2[["key"]], df, on = "key", how ='left')
df = df.dropna()

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

    # BS 찾기
    
    for table in soup.find_all("table"):
        if ''.join(table.text.split()).find("자산") > 0:
            break
        table = BeautifulSoup("<table></table>", features="lxml").table  # 의견 거절 등 BS가 안붙어있을 때 처리
    
    matrix = MatrixGenerator(table)
        
    # Account Parsing

    resultString = ''
    isLine = ''
    
    if len(matrix) > 0:  # BS가 있을 때
        
        exitKey = False
        for i in matrix:
           for j in i:
               matchesPos = ["유동자산", "流動資産"]  # 매출/장기매출 ["매출채", "매출금"] 
               matchesNeg = ["기타", "비유동", "매각예정", "非流動", "其他"]  # 매출/장기매출 ["장기매출", "장기성매출", "충당"]
                                             
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
                    
                    if resultString:
                        exitKey = True
                    break
            
           if resultString == '':
               for j in i:
                   matchesPos = ["유동자산합", "流動資産合" ]  # 매출/장기매출 ["매출채", "매출금"] 
                   matchesNeg = ["기타", "비유동", "매각예정", "非流動", "其他"] # 매출/장기매출 ["장기매출", "장기성매출", "충당"]
                                                 
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
                        if resultString:
                            exitKey = True                        
                        break
            
           if exitKey == True:
               break

    elif len(matrix) == 0:  # BS가 없을 때
        resultString = ""
    
    result.append(resultString)

df["account"] = result

df.to_csv("financial_4_currentAsset.txt")
