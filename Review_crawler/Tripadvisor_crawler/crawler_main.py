import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def get_hotel_review(review_list):
    time.sleep(3)
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
                i.send_keys(Keys.ENTER)
        except:
            pass

        hotel_name = driver.find_element_by_css_selector('h1._1mTlpMC3').text
        hotel_address = driver.find_element_by_xpath('//*[@id="component_4"]/div/div[1]/div[2]/div/div[2]/div/div[1]/div/span[2]/span').text

        comment_tags = [driver.find_elements_by_css_selector('span._3cjYfwwQ'), # Hotel Rating
                        driver.find_elements_by_css_selector('div._2fxQ4TOx'), # Date
                        driver.find_elements_by_xpath('//*[@id="component_14"]/div/div[3]/div[4]/div[3]/div[1]/div/span'), # Review Rating
                        driver.find_elements_by_css_selector('div.glasR4aX'), # Review Title
                        driver.find_elements_by_css_selector('q.IRsGHoPm')  # review plain txt
                        ]

        for hr, d, rr, rt, rpt in zip(*comment_tags):
            review_list.append([hotel_name, hotel_address, float(hr.text)*2, preprocessing_date(d.text), float(rr.get_attribute('class')[-2:])/5, rt.text, rpt.text])
        try:
            next_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located([By.CSS_SELECTOR, 'a.nav.next']))  # next page
            next_btn.send_keys(Keys.ENTER)
        except:
            break
        if page == 2:  # 테스트, 2페이지만
            break
        time.sleep(1)

def preprocessing_date(date):
    try :
        tmp = re.compile(r'\d\d\d\d년 \d\d월').search(date).group()
        year, mon = tmp.split("년")
        return year + "-" + mon[1:3]
    except:
        return str(now_date.tm_year) + "-" + str(now_date.tm_mon)


now_date = time.localtime(time.time())

url = 'https://www.tripadvisor.co.kr/Hotels-g294197-Seoul-Hotels.html'
options = ChromeOptions()
options.add_argument('headless')

driver = Chrome("chromedriver", options=options)
driver.set_window_size(2560,1440)
driver.get(url)

page_idx = 1

while True:
    review_list = []
    hotel_name_list = []
    hotel_name_xpath = '//*[@id="property_7686969"]'
    hotel_name = driver.find_elements_by_xpath('//*[@id="property_7686969"]')
    page = driver.find_elements_by_css_selector('a.review_count')
    idx = 0

    for i in hotel_name:
        hotel_name_list.append(i.text)

    # 현재 page에서 보이는 모든 호텔들 다 클릭 후 새창 띄우기
    for i in range(len(page)):
        time.sleep(5)
        try:
            page[idx].send_keys(Keys.ENTER)
        except:
            page = driver.find_elements_by_css_selector('a.review_count')
            page[idx].send_keys(Keys.ENTER)

        time.sleep(5)

        driver.switch_to.window(driver.window_handles[-1])
        get_hotel_review(review_list)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        idx += 1

    try:
        time.sleep(5)
        next_btn_xpath = '//*[@class="unified ui_pagination standard_pagination ui_section listFooter"]/a'
        next_btn = driver.find_elements_by_xpath(next_btn_xpath)  # next page
        next_btn[-1].send_keys(Keys.ENTER)
        time.sleep(5)

    except:
        break

    page_idx += 1
    print(hotel_name_list)

    # Error control이 100% 되기는 힘드니, page별로 나눠 csv 생성성
    df = pd.DataFrame(review_list)
    df.to_csv(f'../csv_output/Tripadvisor{page_idx}.csv',
              index=False,
              header=["HotelName", "HotelAddress", "HotelRating", "ReviewDate", "ReviewRating", "ReviewTitle",
                      "ReviewText"])

driver.close()
