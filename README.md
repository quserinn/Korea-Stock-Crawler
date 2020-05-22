# Korea-Stock-Crawler

## 환경
- Anaconda
- Windows 10
- Chrome 8.3

## Prerequisites
- 종목 코드 파일 : [여기서](http://marketdata.krx.co.kr/mdi#document=040601) Excel 파일 다운

## Naver Crawler
- 원본 데이터 주소 : "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930"
- 원본 html에 데이터가 있는 것이 아니라 javascript로 불러오기 때문에 `selenium`의 `webdriver`로 페이지를 열어서 데이터를 긁어옴
- Chrome 8.3 버전에 맞는 Chrome Driver 사용. [다운 링크](https://chromedriver.storage.googleapis.com/index.html?path=83.0.4103.39/)

## CompanyGuide Crawler
- 원본 데이터 주소 : http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A005930&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701

## Usage 
```
cr = Crawler(fin_data_dir="fin_data", price_data_dir="price_data", firm_data_path="data.xls")
```
- `fin_data_dir`로 지정한 디렉토리에 재무제표를 각 종목마다 파일 하나씩 생성
- `price_data_dir`로 지정한 디렉토리에 가격 정보 파일 생성
- `firm_data_path` 저장한 종목 데이터 파일
```
cr.download_and_save_all_fin-data()
```
- 재무제표 데이터 저장
```
cr.get_total_price_df()
```
- 가격 정보 저장
