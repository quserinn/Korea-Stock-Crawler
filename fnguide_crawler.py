from datetime import datetime
import os
import time

import bs4
import numpy as np
import pandas as pd
import requests
import tqdm

class NoDataError(Exception):
    def __init__(self, message):
        self.message = message

class Crawler:
    def __init__(self, fin_data_dir="fin_data", price_data_dir="price_data", firm_data_path="data.xls", chrome_driver_path="chromedriver.exe"):
        self.base_url = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode={}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701"
        self.price_base_url = "https://fchart.stock.naver.com/sise.nhn?requestType=0&symbol={}&timeframe={}&count={}"
        self.fin_data_dir = fin_data_dir
        self.price_data_dir = price_data_dir
        self.firm_data_path = firm_data_path
        self.firm_datas = self.read_all_firm_data()
        self.firm_codes = self.firm_datas["종목코드"]

    def read_all_firm_data(self):
        firm_datas = pd.read_excel(self.firm_data_path)
        firm_datas = firm_datas[["종목코드", "기업명", "업종코드", "상장주식수(주)"]]
        firm_datas["종목코드"] = firm_datas["종목코드"].apply(lambda code: 'A' + '0'*(6-len(str(code))) + str(code))

        return firm_datas

    def get_fin_df(self, firm_code, download=False):
        
        file_path = self.fin_data_dir + "/" + str(firm_code) + ".csv"
        
        if os.path.isfile(file_path) and not download:
            return pd.read_csv(file_path)

        html = requests.get(self.base_url.format(firm_code)).text
        soup = bs4.BeautifulSoup(html, 'html.parser')
        fin_info = soup.select('#highlight_D_A')[0]

        col_data = [item.get_text() if len(item.get_text()) == 7 else item.get_text()[-12:-5] for item in fin_info.select('thead th')]
                
        col_index = col_data[3:13]
        row_index = [item.find('dt').get_text().strip() if item.dt else item.get_text().strip() for item in fin_info.select('tbody th')]

        fin_data = [item.get_text().strip() for item in fin_info.select('td')]
        fin_data = np.array(fin_data)
        fin_data.resize(len(row_index), len(col_index))

        fin_df = pd.DataFrame(data=fin_data[0:,0:], index=row_index, columns=col_index)
        
        
        if not os.path.exists(self.fin_data_dir):
            os.makedirs(self.fin_data_dir)
        fin_df.to_csv(file_path, encoding='utf-8-sig')
        
        return fin_df
    
    def download_and_save_all_fin_data(self):
        for code in tqdm.tqdm(self.firm_codes):
            try:
                self.get_fin_df(code, download=True)
            except NoDataError:
                continue
            except requests.exceptions.Timeout:
                time.sleep(60)
                self.get_fin_df(code, download=True)
            except requests.exceptions.ConnectionError:
                time.sleep(60)
                self.get_fin_df(code, download=True)
            except ValueError:
                continue
            except KeyError:
                continue
            except IndexError:
                continue

    def get_price_df(self, code, timeframe='day', count='1500'):
        url = self.price_base_url.format(code, timeframe, count)
        price_info = requests.get(url).text
        bs = bs4.BeautifulSoup(price_info, 'lxml')
        item_list = bs.find_all('item')
        
        date_list = [item['data'].split('|')[0] for item in item_list]
        price_list = [item['data'].split('|')[4] for item in item_list]

        price_df = pd.DataFrame({code:price_list}, index=date_list)

        return price_df

    def get_total_price_df(self):
        date = datetime.now().strftime("%y%m%d")
        file_name = self.price_data_dir + "/" + date + ".csv" 
        if os.path.isfile(file_name):
            return pd.read_csv(file_name)

        total_price_df = self.get_price_df(self.firm_codes[0])
        for code in tqdm.tqdm(self.firm_codes[1:]):
            try:
                price_df = self.get_price_df(code)
                total_price_df = pd.merge(total_price_df, price_df, how='outer', right_index=True, left_index=True)
            except requests.exceptions.Timeout:
                time.sleep(60)
                price_df = self.get_price_df(code)
            except requests.exceptions.ConnectionError:
                time.sleep(60)
                price_df = self.get_price_df(code)
            except ValueError:
                continue
            except KeyError:
                continue

        total_price_df.index = pd.to_datetime(total_price_df.index)
        
        if not os.path.exists(self.price_data_dir):
            os.makedirs(self.price_data_dir)
        total_price_df.to_csv(file_name)
        return total_price_df