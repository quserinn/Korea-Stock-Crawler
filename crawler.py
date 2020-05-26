import os
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

class Crawler:
    def __init__(self):
        self.fn_guide_url = "http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode={}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=&strResearchYN="
        self.naver_url = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}"
        self.price_base_url = "https://fchart.stock.naver.com/sise.nhn?requestType=0&symbol={}&timeframe={}&count={}"

    def save_base_comp_data(self, save_path="comp_data.csv", ori_data_path="data.xls"):
        def build_code(code):
            return '0'*(6-len(str(code))) + str(code)

        comp_data = pd.read_excel(ori_data_path)
        comp_data = comp_data[['종목코드', '기업명', '업종', '상장주식수(주)']]
        comp_data['종목코드'] = comp_data['종목코드'].apply(build_code)
        comp_codes = comp_data['종목코드']

        common_shares = []
        prefered_shares = []
        floating_shares = []
        treasury_stocks = []

        for code in tqdm(comp_codes, desc="회사 기본 데이터 크롤링"):
            url = self.fn_guide_url.format('A' + code)
            try:
                html = requests.get(url).text
            except requests.exceptions.ConnectionError:
                time.sleep(60)
                html = requests.get(url).text
            soup = BeautifulSoup(html, 'lxml')
            mp_table = soup.select("#svdMainGrid1 tbody td")
            num_shares = mp_table[-2].get_text().split('/')
            num_floating_shares = mp_table[-1].get_text().split('/')[0]
            common_shares.append(num_shares[0])
            prefered_shares.append(num_shares[1])
            floating_shares.append(num_floating_shares)
            try:
                treasury_stock = soup.select("#svdMainGrid5 table tbody tr:nth-child(5) td:nth-child(3)")[0].get_text()
                treasury_stocks.append(treasury_stock)
            except IndexError:
                treasury_stocks.append('0')
              
        comp_data['발행주식수(보통)'] = common_shares
        comp_data['발행주식수(우선)'] = prefered_shares
        comp_data['유동주식수'] = floating_shares
        comp_data['자기주식수'] = treasury_stocks
        comp_data.set_index('종목코드', inplace=True, drop=True)
        comp_data.to_csv(save_path, encoding='utf-8-sig', sep='\t')

    def save_financial_data(self, comp_data_path="comp_data.csv", save_path_dir="financial_data", chrome_driver_path="chromedriver.exe"):
        if not os.path.exists(save_path_dir):
            os.makedirs(save_path_dir)
        
        driver = webdriver.Chrome(executable_path=chrome_driver_path)
        comp_codes = pd.read_csv(comp_data_path, sep='\t', dtype={'종목코드': str})['종목코드']
        for code in tqdm(comp_codes, desc="재무제표 데이터 크롤링"):
            file_path = save_path_dir + '/' + code + '.csv'
            driver.get(self.naver_url.format(code))
            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')
            parent_div = soup.find("div", {"id": lambda l: l and len(l) == 10})
            if not parent_div:
                continue
            
            fin_info = parent_div.find_all("table")[1]

            col_data = [item.get_text().strip()[:7] for item in fin_info.select('thead th')]                    
            col_index = col_data[3:13]
            row_index = [item.get_text().strip() for item in fin_info.select('tbody th.bg')]

            fin_data = [item.get_text().strip() for item in fin_info.select('td')]
            fin_data = np.array(fin_data)
            fin_data.resize(len(row_index), len(col_index))

            fin_df = pd.DataFrame(data=fin_data[0:,0:], index=row_index, columns=col_index)

            fin_df.to_csv(file_path, sep='\t', encoding='utf-8-sig')
        
    def save_total_price_data(self, comp_data_path="comp_data.csv", save_path="total_price.csv"):
        comp_codes = pd.read_csv(comp_data_path, sep='\t', dtype={'종목코드': str})['종목코드']
        
        total_price_df = self.get_price_df((comp_codes[0]))
        for code in tqdm(comp_codes[1:], desc="모든 가격 데이터 크롤링"):
            try:
                price_df = self.get_price_df(code)
                total_price_df = pd.merge(total_price_df, price_df, how='outer', right_index=True, left_index=True)
            except requests.exceptions.ConnectionError:
                time.sleep(60)
                price_df = self.get_price_df(code)
            except ValueError:
                continue
            except KeyError:
                continue
        
        total_price_df.index = pd.to_datetime(total_price_df.index)
        total_price_df.to_csv(save_path, sep='\t', encoding='utf-8-sig')

    def get_price_df(self, code, timeframe='day', count='1500'):
        url = self.price_base_url.format(code, timeframe, count)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        item_list = soup.find_all('item')
        
        date_list = [item['data'].split('|')[0] for item in item_list]
        price_list = [item['data'].split('|')[4] for item in item_list]

        price_df = pd.DataFrame({code:price_list}, index=date_list)

        return price_df   

    def save_last_data(self, comp_data_path='comp_data.csv', save_path_dir="last_data"):
        if not os.path.exists(save_path_dir):
            os.makedirs(save_path_dir)
        
        comp_codes = pd.read_csv(comp_data_path, sep='\t', dtype={'종목코드': str})['종목코드']
        date = datetime.now().strftime("%y%m%d")
        file_path = save_path_dir + '/' + date + '.csv'
        
        prices = []
        trades = []
        for code in tqdm(comp_codes[:10], desc="최근 종가와 거래량 크롤링"):
            url = self.naver_url.format(code)
            try:
                html = requests.get(url).text
            except requests.exceptions.ConnectionError:
                time.sleep(60)
            soup = BeautifulSoup(html, 'lxml')
        
            try:
                price = soup.select("#cTB11 tbody tr:nth-child(1) td strong")[0].get_text().strip()
                trade = soup.select("#cTB11 > tbody > tr:nth-child(4) > td")[0].get_text().split('/')[0].strip()[:-1]
                
            except IndexError:
                price = '100000000'
                trade = '0'
            prices.append(price)
            trades.append(trade)
        df = pd.DataFrame({'종목코드': comp_codes[:10], '종가': prices, '거래량': trades})
        df.set_index('종목코드', inplace=True, drop=True)
        df.to_csv(file_path, encoding='utf-8-sig', sep='\t')
