from selenium import webdriver
from konlpy.tag import Okt
from nltk import Text
from matplotlib import font_manager, rc
from wordcloud import WordCloud
from collections import Counter
from tqdm import tqdm

import matplotlib.pyplot as plt
import time
import warnings
import pandas as pd

# xpath 사용 시 등장하는 deprecation warning 해제
warnings.filterwarnings(action="ignore")

"""
############ 데이터 수집 - 웹 크롤링 ############
"""

path = "chromedriver.exe" # 크롭 웹 드라이버 경로 지정

options = webdriver.ChromeOptions()
options.add_argument('headless') # 백그라운드 실행

driver = webdriver.Chrome(path, chrome_options=options) # 드라이버 경로 지정
url_list = [] # 블로그 url 저장
content_list = "" # 블로그 컨텐츠 누적 변수
text = "던파 복귀" # 검색어
#text = "던파 BGM"

# 1~500 페이지 블로그의 링크 추출
for i in tqdm(range(1,501), desc = '블로그 링크 추출'):
    url = 'https://section.blog.naver.com/Search/Post.nhn?pageNo=' + str(i) + '&rangeType=ALL&orderBy=sim&keyword=' + text
    driver.get(url)
    time.sleep(0.5) # 오류 방지

    for j in range(1,3):
        titles = driver.find_element_by_xpath('/html/body/ui-view/div/main/div/div/section/div[2]/div['+str(j)+']/div/div[1]/div[1]/a[1]')
        title = titles.get_attribute('href')
        url_list.append(title)


print("\n블로그 url 수집 완료, 해당 url 데이터 크롤링\n")

# 링크 추출된 블로그들 순회하며 블로그 내의 내용 크롤링
try:
    for url in tqdm(url_list, desc = '블로그 내용 크롤링'):
        driver.get(url)
        driver.switch_to.frame("mainFrame")
        overlays = ".se-component.se-text.se-l-default" # 내용 크롤링
        contents = driver.find_elements_by_css_selector(overlays)

        for content in contents:
            content_list = content_list + content.text # 각 블로그 내용 누적
except Exception as e:
    print("예외 발생 : ",e)

"""
############ 크롤링된 데이터 정제 - 명사 추출 및 불용어 제거 ############
형태소 분석기 Okt를 사용하여 수집한 데이터 중 명사만 추출
기본 조사 및 데이터 분석 시 의미 없는 데이터 제거 
Ex. 던파, 1호기, 몇 일차 등 검색 시 "던파 복귀"에 관한 검색 시 불가피하게 등장하는 단어들 제거
"""

# 형태소 분석기 Okt 사용
okt = Okt()
myList = okt.pos(content_list, norm=True, stem=True)  # 모든 형태소 추출
myList_filter = [x for x, y in myList if y in ["Noun"]]  # 추출된 값 중 명사만 추출
Okt_before = Text(myList_filter, name="Okt")

# 데이터 정제 전 데이터 개수
freq = Counter(Okt_before).most_common()
print("데이터 정제 전 데이터 개수 : " , len(Okt_before))

with open('data/stopwords.txt','r') as f:
    list_file = f.readlines()

stopwords = list_file[0].split(",") # 콤마로 구분
remove_wordList = [x for x in Okt_before if x not in stopwords]
Okt_after = Text(remove_wordList, name="Okt")
freq_before = Counter(Okt_after).most_common()

# 데이터 정제 완료
print("데이터 정제 후 데이터 개수 : " , len(Okt_after))

"""
############ 데이터 시각화 ############
"""
# 그래프 한글 출력 인코딩
font_location = "c:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_location).get_name()
rc('font', family=font_name)

# 그래프 x, y 라벨 설정
plt.xlabel("던파 복귀 관련 명사")
plt.ylabel("빈도수")

# 그래프 x, y 값을 설정
wordInfo = dict()
for tags, counts in Okt_after.vocab().most_common(50):
    if (len(str(tags)) > 1):
        wordInfo[tags] = counts

values = sorted(wordInfo.values(), reverse=True)
keys = sorted(wordInfo, key=wordInfo.get, reverse=True)

# matplotlib 그래프 값 설정
plt.bar(range(len(wordInfo)), values, align='center')
plt.xticks(range(len(wordInfo)), list(keys), rotation='100')
plt.title('던파 복귀 검색어에 대한 명사 별 빈도수')
plt.show()

# wordcloud 출력
wc = WordCloud(width = 1000, height = 1000, background_color = "white", colormap = 'autumn', font_path = font_location, max_words = 50)
plt.imshow(wc.generate_from_frequencies(Okt_after.vocab()))
plt.axis("off")
plt.show()

# Dataset 내보내기
dataset = pd.DataFrame(list(Okt_after),columns=['추출한 명사'])
dataset.to_excel('df_blog_crawling.xlsx',encoding='',index=False)
