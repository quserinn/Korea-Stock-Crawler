from data_manager import DataManager
from s_rim import SRIM

dm = DataManager(fin_data_dir="fin_data_naver")
fin_data, firm_codes = dm.load_all_fin_data()
firm_data = dm.firm_datas
srim = SRIM(fin_data, firm_data, firm_codes, index_date="2019")
srim.get_s_rim_all()
while True:
    code = input("종목코드를 입력하세요\n")
    print(srim.get_s_rim(code))