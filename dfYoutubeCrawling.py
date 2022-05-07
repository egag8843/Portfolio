from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as bs


import pandas as pd
import time
import warnings

# tag_name 사용 시 등장하는 deprecation warning 해제
warnings.filterwarnings(action='ignore')

"""
############ 데이터 수집 - 웹 크롤링 ############
"""

text = '"던파" 추억' # 검색어, 명확한 유튜브 검색을 위해 ""로 묶음.
path = "chromedriver.exe" # 크롬 웹 드라이버 경로 지정
url = 'https://www.youtube.com/results?search_query=' + text # 유튜브 url 지정

options = webdriver.ChromeOptions()
options.add_argument('headless') # 백그라운드 실행

driver = webdriver.Chrome(path, chrome_options=options)
driver.get(url)

# 페이지 정보가 있는 body 태그 추출
body = driver.find_element_by_tag_name('body')

for i in range(1,100): # body 태그를 통해 페이지를 내리며 검색
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.3) # 오류방지

# soup를 통해 데이터 가져오기
soup = bs(driver.page_source, 'lxml')

# 제목, 주소, 조회수가 포함된 a#video-title 추출
title = soup.select('a#video-title')
view = soup.select('a#video-title')

title_list = []
view_list = []

for i in range(len(title)): # 제목과 조회수를 리스트에 저장
    title_list.append(title[i].text.strip())

    # 'aria-label' 속성에서 문자열 나눈 후 마지막 값 사용, 정수형 변환을 위해 텍스트 자름.
    view_list.append(view[i].get('aria-label').split()[-1].strip('회').replace(',',''))

# 조회수가 '재생'인 결측값 0으로 변환
for index, value in enumerate(view_list):
    if value == '재생':
        view_list[index] = 0

# Int 형변환 및 정렬
view_int = list(map(int, view_list))
view_res = sorted(view_int, reverse=True)

# 추출한 제목과 조회수 딕셔너리에 저장
youtubeDic = {
    '제목':title_list,
    '조회수':view_res
}

#Dataset 내보내기
df = pd.DataFrame(youtubeDic)
df.to_excel('youtube_crawling.xlsx', encoding='',index=False)








