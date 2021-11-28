import os
import time
from lxml import etree
import pandas as pd
import requests
import random
import re
import xlrd


def switch_v2ray():
    os.system("killall -e v2ray")
    os.system(
        "nohup ./v2ray-linux/v2ray -config ./v2ray_config/config%d.json &" % random.randint(1, 25))
    time.sleep(0.5)


def get_final_result(url):
    retry_num = 0
    result_num = 0
    while retry_num < 3:
        try:
            result_num = get_result_num(url)
        except:
            retry_num += 1
            continue
        else:
            break
    return result_num


def get_result_num(url):
    switch_v2ray()
    res = requests.get(url, headers=headers, proxies=proxy)
    xpath_res = etree.HTML(res.text)
    num = xpath_res.xpath('//div[@id="result-stats"]/text()')
    topstuff = xpath_res.xpath('//div[@id="topstuff"]//b')
    if len(num) == 0:
        raise Exception("can not get num")
    elif len(topstuff) == 0:
        return int(''.join(re.findall(r'\d+', num[0])))
    else:
        return 0


keywords = xlrd.open_workbook('./keywords.xls').sheet_by_index(0).col_values(0,
                                                                                 start_rowx=0)
key = ['keyword', 'result']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
}
proxy = {
    'http': "127.0.0.1:1087",
    'https': "127.0.0.1:1087"
}

google_result = []
try:
    for keyword in keywords:
        value = [keyword]
        keyword.replace(' ', '+')
        url = f'https://www.google.com/search?q="{keyword}"'
        value.append(get_final_result(url))
        df = pd.DataFrame(data=dict(zip(key, value)), index=[0])
        google_result.append(df)
finally:
    os.system("killall -e v2ray")
    sheet = pd.concat(google_result)
    sheet.to_excel('./google_result.xls', index=False)
