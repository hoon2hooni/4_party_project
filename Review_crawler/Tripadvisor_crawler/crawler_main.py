import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import bs4
import csv
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

review_list = []

def get_hotel_review(review_list):
    page = 0

    comment_tags = [driver.find_elements_by_css_selector('h1._1mTlpMC3'),  # Hotel name
                    driver.find_elements_by_css_selector('q.IRsGHoPm'),  # review plain txt
                    driver.find_elements_by_css_selector('div._1EpRX7o3'),  # Location, Posting, Num of Reviews
                    driver.find_elements_by_css_selector('div._2fxQ4TOx')]  # ID, Date

    while True:
        page += 1
        # 더보기 전부 클릭
        more_btns = driver.find_elements_by_css_selector('span._3maEfNCR')
        try:
            for i in more_btns:
                i.click()
        except:
            pass

        hotel_name = driver.find_element_by_css_selector('h1._1mTlpMC3').text
        hotel_address = driver.find_element_by_xpath('//*[@id="component_4"]/div/div[1]/div[2]/div/div[2]/div/div[1]/div/span[2]/span').text

        comment_tags = [driver.find_elements_by_css_selector('span._3cjYfwwQ'), # Hotel Rating
                        driver.find_elements_by_css_selector('div._2fxQ4TOx'), # Date
                        driver.find_elements_by_css_selector('div.nf9vGX55'), # Review Rating
                        driver.find_elements_by_css_selector('div.glasR4aX'), # Review Title
                        driver.find_elements_by_css_selector('q.IRsGHoPm')  # review plain txt
                        ]

        for hr, d, rr, rt, rpt in zip(*comment_tags):
            review_list.append([hotel_name, hotel_address, float(hr.text)*2, d.text, rr.get_attribute("span"), rt.text, rpt.text])
        try:
            next_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located([By.CSS_SELECTOR, 'a.nav.next']))  # next page
            next_btn.click()
        except:
            break
        if page == 2:  # 테스트, 2페이지만
            break
        time.sleep(1)

url = 'https://www.tripadvisor.co.kr/Hotels-g294197-Seoul-Hotels.html'
options = ChromeOptions()
options.add_argument('headless')

driver = Chrome("chromedriver", options=options)
driver.set_window_size(1920,1080)
driver.get(url)

while True:
    # 현재 page의 호텔 클릭
    page = driver.find_elements_by_css_selector('a.review_count')

    for i in page:
        time.sleep(5)
        i.click()
        driver.switch_to.window(driver.window_handles[-1])
        get_hotel_review(review_list)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        for row in review_list:
            print(row)

    try:
        next_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located([By.CSS_SELECTOR, 'a.nav.next']))  # next page
        next_btn.click()
    except:
        print('finish')

"""

f = open(f'..\csv_output\Tripadvisor_{search}.csv', 'w', encoding='utf-8', newline='') # csv 생성 준비
csvWriter = csv.writer(f) # writer



comment_list = list(map(list, zip(*comment_list))) # for transpose

for i in comment_list:
    csvWriter.writerow(i) # csv에 write

f.close() # file close
"""