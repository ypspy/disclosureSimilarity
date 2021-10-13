# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 13:52:19 2021

@author: https://blog.naver.com/ellijahbyeon/222213048898
"""

import requests
import pandas as pd
from io import BytesIO
from tqdm.notebook import tqdm

path = "C:\data\\stockinfo\\"

def krx_basic(tdate):
    gen_req_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    query_str_parms = {
        'mktId': 'ALL',
        'trdDd': str(tdate),
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01501'
    }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36' #generate.cmd에서 찾아서 입력하세요
    }
    r = requests.get(gen_req_url, query_str_parms, headers=headers)
    gen_req_url = 'http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd'
    form_data = {
        'code': r.content
    }
    r = requests.post(gen_req_url, form_data, headers=headers)
    df = pd.read_excel(BytesIO(r.content))
    df['일자'] = tdate
    file_name = 'basic_'+ str(tdate) + '.xlsx'
    df.to_excel(path+file_name, index=False, index_label=None)
    # print('KRX crawling completed :', tdate)
    return

for year in tqdm(range(1997, 1999)):
    for month in tqdm(range(1, 13), leave=False):
        for day in tqdm(range(1, 32), leave=False):
            tdate = year * 10000 + month * 100 + day * 1
            if tdate <= 20211231:
                krx_basic(tdate)