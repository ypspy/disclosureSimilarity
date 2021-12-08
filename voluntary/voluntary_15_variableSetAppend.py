# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 22:24:09 2021

@author: yoonseok
"""

import pandas as pd
import os

df = pd.read_csv(r"C:\data\financials\h2_variables.txt")
df2 = pd.read_csv(r"C:\data2\voluntary.h2_variables.txt")

df3 = df.append(df2, ignore_index=True)

# Remove duplicates
df3["duplc"] = df3.duplicated(subset=["key"], keep=False)
isTrue1 = df3[df3["duplc"] == True]

df3 = df3.drop_duplicates(subset=["key"])
df3 = df3.drop(["duplc"], axis=1)

dupl = []
for i in range(len(df3)):
    dupl.append(str(df3.iloc[i,1])+str(df3.iloc[i,2]))
df3["dupl"] = dupl
df3["duplc"] = df3.duplicated(subset=["dupl"], keep=False)
isTrue2 = df3[df3["duplc"] == True]

df3 = df3.drop_duplicates(subset=["dupl"])
df3 = df3.drop(["duplc", "dupl"], axis=1)

# Change to datafolder
os.chdir(r"C:\data2")

df3.to_csv("h2_variables_append.txt")
