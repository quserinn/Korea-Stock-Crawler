from data_manager import DataManager

import pandas as pd
import tqdm
import numpy as np

def next_year(year_str):
    return str(int(year_str[:4]) + 1) + year_str[4:]

class SRIM:
    def __init__(self, fin_data, firm_data, firm_codes, required_rate=8, index_date="2019"):
        self.fin_data = fin_data
        self.firm_data = firm_data
        self.firm_codes = firm_codes
        self.required_rate = required_rate
        self.index_date = index_date

        pd.options.display.float_format = '{:,.2f}'.format

    def get_s_rim(self, code):
        code_df = self.srim_df.loc[code]
        return code_df

    
    def get_s_rim_all(self):
        total_df = []
        for code in self.firm_codes:
            temp_df = self.build_df(code, self.index_date)
            if temp_df is None:
                continue
            total_df.append(temp_df)
        total_df = pd.DataFrame(total_df)
        total_df['SRIM'] = (total_df['자본총계'] + total_df['자본총계']*(total_df['ROE'] - self.required_rate) / self.required_rate)*100000000
        total_df['적정주가'] = total_df['SRIM'] / total_df['발행주식수']
        total_df.set_index("종목번호", inplace=True)
        self.srim_df = total_df
        return total_df
    
    def build_df(self, code, year):
        try:
            data = self.fin_data[code]
            negative_debt = data.loc["자본총계(지배)", year]
            ROE = data.loc["ROE(%)", str(int(year) + 1)]
            if np.isnan(ROE):
                ROE = (data.loc["ROE(%)", year]*3 + data.loc["ROE(%)", str(int(year) - 1)]*2 + data.loc["ROE(%)", str(int(year) - 2)])/6
            try:
                shares = float(self.firm_data.loc[code, "발행주식수(보통)"]) + float(self.firm_data.loc[code, "발행주식수(우선)"])
            except ValueError:
                shares = float(self.firm_data.loc[code, "상장주식수(주)"])
            return {"종목번호": code, "자본총계": negative_debt, "ROE": ROE, "발행주식수": shares}
        except KeyError:
            return None
        except ValueError:
            return None