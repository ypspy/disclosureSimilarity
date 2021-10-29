# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 23:41:42 2021

@author: yoonseok
"""

import OpenDartReader
import pandas as pd
import os

# Change to datafolder
os.chdir(r"C:\data\car\\")

api_key = '7f6ee52d85573132981012eb8a73ab95a4aaa86b'
dart = OpenDartReader(api_key) 

rct3 = pd.date_range(start='19990101', end='20210901')
dt_list = rct3.strftime("%Y%m%d").to_list()

num = 0

reportType = 'E'
reportList = dart.list(start=dt_list[50 * num],
                       end=dt_list[50 * (num + 1)],
                       kind=reportType)    

while True:
    num += 1
    print("{0} {1}".format(num, ' '))
    try:
        reportList = reportList.append(dart.list(start=dt_list[50 * num],
                                                 end=dt_list[50 * (num + 1)],
                                                 kind=reportType)
                                       )
    except:
        reportList = reportList.append(dart.list(start=dt_list[50 * num],
                                                 end=dt_list[-1],
                                                 kind=reportType)
                                       )
        break

reportList.to_csv("car_1_reportTypeE_list.csv")
