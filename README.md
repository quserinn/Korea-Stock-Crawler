# Korea-Stock-Crawler

## 환경
- Anaconda
- Windows 10
- Chrome 8.3

## Prerequisites
- 종목 코드 파일 : [여기서](http://marketdata.krx.co.kr/mdi#document=040601) Excel 파일 다운(csv로 받으면 파일이 깨지는 현상 있음)
- Chromedriver
  - 재무제표 데이터를 크롤링할 때는 원본 html에 데이터가 있는 것이 아니라 javascript로 불러오기 때문에 `selenium`의 `webdriver`로 페이지를 열어서 데이터를 긁어옴
  - 설치된 크롬 브라우저 버전에 맞는 드라이버 설치 [다운 링크](https://chromedriver.storage.googleapis.com/index.html?path=83.0.4103.39/)

## Usage 
### 회사 정보 저장
- company guide에서 크롤링
- 앞에서 받은 종목 코드 파일(`data.xls`)을 기반으로 발행주식수, 유동주식수, 자기주식수 정보를 받아와서 새 파일로 저장
- 다른 데이터를 크롤링 하기전에 선행되어야함
```
cr = Crawler()
cr.save_base_comp_data(save_path='comp_data.csv', ori_data_path='data.xls')
```

### 재무제표 데이터 저장
- 네이버 증권에서 크롤링해서 회사마다 csv 파일 하나씩 생성
```
cr = Crawler()
cr.save_financial_data(comp_data_path='comp_data.csv', save_path_dir='financial_data', chrome_driver_path='chromedriver.exe')
```

### 모든 가격 정보 저장
- 네이버 증권에서 크롤링
```
cr = Crawler()
cr.save_totla_price_data(comp_data_path='comp_data.csv', save_path='total_price.csv'
```

### 당일 종가 및 거래량 저장
- 네이버 증권에서 크롤링
```
cr = Craweler()
cr.save_last_data(comp_data_pth='comp_data.csv', save_path_dir='last_data'
```

## 결과 화면 예시
TODO
