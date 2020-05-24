from naver_crawler import Crawler

from datetime import datetime
import os
import time

import bs4
import pandas as pd
import requests
import tqdm
import numpy as np

date = datetime.now().strftime("%y%m%d")

class DataManager:
    def __init__(self, fin_data_dir="fin_data", price_data_dir="price_data", firm_data_path="data.xls"):
        self.cr = Crawler(fin_data_dir, price_data_dir, firm_data_path)
        
        self.firm_datas = self.cr.firm_datas
        self.firm_datas.set_index("종목코드", drop=True, inplace=True)
        self.firm_codes = self.cr.firm_codes

        self.fin_data_dir = fin_data_dir
        self.price_data_dir = price_data_dir

    def load_all_fin_data(self):
        if not os.path.exists(self.fin_data_dir):
            self.cr.download_and_save_all_fin_data()

        codes = []
        datas = []
        print("모든 재무제표 데이터를 불러옵니다")
        for code in tqdm.tqdm(self.firm_codes):
            data = self.load_fin_data(code)
            if data is not None:
                codes.append(code)
                datas.append(data)
        
        self.fin_datas = pd.Series(datas, index=codes)
        return self.fin_datas, codes
    
    def load_fin_data(self, code):
        file_path = self.fin_data_dir + "/" + str(code) + ".csv"
        if not os.path.isfile(file_path):
            return None
        data = pd.read_csv(file_path, sep='\t', thousands=',', index_col=0)
        data.rename(columns = lambda x: x[:4] if x in data.columns[:4] else x, inplace=True)
        return data
    
    def load_all_price_data(self):
        data_path = self.price_data_dir + "/" + date
        if not os.path.exists(data_path):
            self.price_data = self.cr.get_total_price_df
        else:
            self.price_data = pd.read_csv(data_path)
        return self.price_data

    def save_num_shares(self, new_firm_data_path):
        if "유동주식수" in self.firm_datas.columns:
            print("이미 유동주식수가 있습니다")
            return
        common_shares = []
        prefered_shares = []
        floating_shares = []
        base_url = "http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode={}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=&strResearchYN="

        print("data_manager : 모든 종목 주식수 다운")
        for code in tqdm.tqdm(self.firm_codes):
            url = base_url.format('A' + code)
            try:
                html = requests.get(url).text
            except requests.exceptions.ConnectionError:
                time.sleep(60)
                html = requests.get(url).text
            soup = bs4.BeautifulSoup(html, 'html.parser')
            table_hb = soup.select("#svdMainGrid1 tbody td")
            num_floating_shares = table_hb[-1].get_text().split("/")[0]
            num_shares = table_hb[-2].get_text().split("/")
            common_shares.append(num_shares[0])
            prefered_shares.append(num_shares[1])
            floating_shares.append(num_floating_shares)
        temp = pd.DataFrame({'유동주식수': floating_shares, '발행주식수(보통)': common_shares, '발행주식수(우선)': prefered_shares})
        temp.to_csv("test.csv", sep='\t')
        self.firm_datas.reset_index(drop=True, inplace=True)
        self.firm_datas = pd.concat([self.firm_datas, temp], axis=1)
        self.firm_datas.set_index("종목코드", drop=True, inplace=True)
        self.firm_datas.to_excel(new_firm_data_path)