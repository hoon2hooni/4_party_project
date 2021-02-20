# coding:utf-8

import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def init_page_setting(driver):
    filter_hotel_xpath = '//*[@id="component_10"]/div/div[2]/div[5]/div[2]/div[1]/div/label'
    driver.find_element_by_xpath(filter_hotel_xpath).click()  # 호텔 필터 클릭
    time.sleep(5)

    open_view_box_xpath = '/html/body/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/span[1]/div/div/div[1]'
    driver.find_element_by_xpath(open_view_box_xpath).click()
    time.sleep(1)

    sort_distance_xpath = '/html/body/div[2]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div[2]/span[1]/div/div[2]/div[4]/div'
    driver.find_element_by_xpath(sort_distance_xpath).click()
    time.sleep(5)

def click_hotel_next_btn(driver):
    next_btn_xpath = '//*[@class="unified ui_pagination standard_pagination ui_section listFooter"]/a'
    next_btn = driver.find_elements_by_xpath(next_btn_xpath)  # next page
    next_btn[-1].send_keys(Keys.ENTER)
    time.sleep(5)

def get_hotel_review(driver):
    review_list = []

    hotel_name = driver.find_element_by_xpath('//*[@id="HEADING"]').text
    hotel_address = driver.find_element_by_xpath(
        '//*[@id="component_4"]/div/div/div[2]/div/div[2]/div/div/div').text
    hotel_rating = float(driver.find_element_by_css_selector('span._3cjYfwwQ').text)

    while True:

        try:
            # 더보기 버튼 누르기 시도
            more_btn = driver.find_element_by_css_selector('div.XUVJZtom')
            driver.execute_script("arguments[0].click();", more_btn)

        except:
            # 더보기 버튼이 존재하지 않으면 가져올 review가 없으므로 바로 탈출
            driver.close()
            return [[0]]

        time.sleep(1)

        # 추출할 속성들 정리
        comment_tags = [driver.find_elements_by_css_selector('div._2fxQ4TOx'),  # Date
                        driver.find_elements_by_css_selector('div.nf9vGX55'), # Review Rating

                        driver.find_elements_by_css_selector('div.glasR4aX'), # Review Title
                        driver.find_elements_by_css_selector('q.IRsGHoPm')  # review plain txt
                        ]

        # 추출한 속성 review_list에 추가
        for d, rr, rt, rpt in zip(*comment_tags):
            review_list.append([hotel_name, hotel_address, hotel_rating * 2, preprocessing_date(d.text),
                                float(rr.find_element_by_xpath("descendant::span").get_attribute('class')[-2:]) / 5, rt.text, rpt.text])
        # 다음을 누를 수 있으면 다음
        try :
            review_next_btn = driver.find_element_by_css_selector('a.nav.next')
            review_next_btn.click()
            time.sleep(4)

        # 다음을 누를 수 없으므로 탈출
        except:
            break

    driver.close()

    return review_list

def preprocessing_date(date):
    try :
        tmp = re.compile(r'\d\d\d\d년 \d\d월').search(date).group()
        year, mon = tmp.split("년")
        return year + "-" + mon[1:3]
    except:
        return str(now_date.tm_year) + "-" + str(now_date.tm_mon)

# url 접속
url = 'https://www.tripadvisor.co.kr/Hotels-g294197-Seoul-Hotels.html'
options = ChromeOptions()
#options.add_argument('headless')
driver = Chrome("chromedriver", options=options)
driver.set_window_size(2560,1440)
driver.get(url)
time.sleep(5)

# filter, sort 적용
init_page_setting(driver)

page_size = int(driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div/div[2]/div[3]/div[2]/div[9]/div/div/div/div/a[7]').text)

time.sleep(5)

# 리뷰 중 날짜가 최근인 데이터들을 맞춰주기 위해
now_date = time.localtime(time.time())
now_year, now_mon = now_date.tm_year, now_date.tm_mon

# csv 저장 편리하게 하기 위해
page_idx = 1

# hotel 리스트 다음 버튼을 page_size - 1번 누른다
for page_num in range(page_size - 1):

    # 호텔 리스트 페이지에서 리뷰가 있다면 각 호텔 리뷰 페이지로 접속
    hotel_pages = driver.find_elements_by_css_selector('a.review_count')
    hotels_review_list = []
    print(len(hotel_pages))
    for hp_idx in range(len(hotel_pages)):
        # review가 0개보다 클 경우 클릭
        time.sleep(3)
        hotel_pages = driver.find_elements_by_css_selector('a.review_count')
        if hotel_pages[hp_idx].get_attribute('class') == "review_count":
            hotel_pages[hp_idx].send_keys(Keys.ENTER)
            time.sleep(5)
            driver.switch_to.window(driver.window_handles[-1])

            # review가 있는 hotel page에서 review 가져오기 시작
            tmp = get_hotel_review(driver)
            if len(tmp[0]) > 1 :
                hotels_review_list += tmp
            driver.switch_to.window(driver.window_handles[0])

    click_hotel_next_btn(driver)

    df = pd.DataFrame(hotels_review_list)
    df.to_csv(f'../csv_output/Tripadvisor{page_idx}.csv',
              index=False,
              header=["HotelName", "HotelAddress", "HotelRating", "ReviewDate", "ReviewRating", "ReviewTitle",
                      "ReviewText"])

    print(f"csv {page_idx} finished")

    page_idx += 1

driver.close()