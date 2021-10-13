# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 22:39:52 2021

@author: yoonseok
"""

import os
import pandas as pd
from tqdm.notebook import tqdm

def int_only_nums(val):
    try:
        return '%s' % int(val)
    except:
        return val

# 1. 작업 폴더로 변경
os.chdir(r"C:\data\stockinfo\\")  # 작업 폴더로 변경

for year in tqdm(range(1997, 1999), desc="concat"):
    df = pd.read_excel('basic_' + str(year * 10000 + 101) + '.xlsx',
                       index_col=None, header=None)
    df = df[df[7] != '-'][1:]
    for month in tqdm(range(1, 13), leave=False):        
        for day in tqdm(range(1, 32), leave=False):
            tdate = year * 10000 + month * 100 + day * 1
            if tdate != str(year * 10000 + 101):
                dfA = pd.read_excel('basic_' + str(tdate) + '.xlsx',
                                    index_col=None, header=None)
                df = df.append(dfA[dfA[7] != '-'][1:])
    df[0] = df[0].apply(int_only_nums)
    df = df.sort_values(by=[0, 14])
    df[[14,0,1,2,4,10,12,13]].to_csv('stockPrice_' + str(year) + '.csv')

