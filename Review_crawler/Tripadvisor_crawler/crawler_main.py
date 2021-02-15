import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import csv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://www.tripadvisor.co.kr/Hotel_Review-g294197-d306130-Reviews-LOTTE_HOTEL_Seoul-Seoul.html#REVIEWS'
search = "LotteHotel" # 검색어 설정 for csv title
options = ChromeOptions()

options.add_argument('headless')

driver = Chrome("C:/Anaconda3/chromedriver/chromedriver", options=options)
driver.set_window_size(1920,1080)
driver.get(url)


comment_list = [[] for i in range(3)] # range안 인자는 comment_tags의 len만큼
page = 0

f = open(f'Tripadvisor_{search}.csv', 'w', encoding='utf-8', newline='') # csv 생성 준비
csvWriter = csv.writer(f) # writer

while True:
    page += 1
    print(page)
    more_btns = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located([By.CSS_SELECTOR,'span._3maEfNCR']))
    more_btns[0].click()

    time.sleep(1)
    comment_tags = [driver.find_elements_by_css_selector('q.IRsGHoPm'), # review plain txt
                    driver.find_elements_by_css_selector('div._1EpRX7o3'), # Location, Posting, Num of Reviews
                    driver.find_elements_by_css_selector('div._2fxQ4TOx')] # ID, Date

    for idx, tags in enumerate(comment_tags):
        for tag in tags:
            comment_list[idx].append(tag.text) # comment_list에 crawling 한 내용 추가

    next_btn = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located([By.CSS_SELECTOR,'a.nav.next'])) # next page
    try:
        next_btn.click()
    except:
        print('finish')
        break
    if page == 5: # 테스트, 5페이지만
        break
    time.sleep(1)

comment_list = list(map(list, zip(*comment_list))) # for transpose

for i in comment_list:
    print(i)
    csvWriter.writerow(i) # csv에 write

f.close() # file close
