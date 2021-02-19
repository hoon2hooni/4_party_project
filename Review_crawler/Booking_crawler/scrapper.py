import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import time

path = "D:\\다운로드\\chromedriver_win32\\chromedriver.exe"
url = "https://www.booking.com/"

# options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--window-size=1920x1080')

def search():
    search_text = browser.find_element_by_id("ss")
    search_button = browser.find_element_by_class_name("sb-searchbox__button")

    search_text.send_keys("서울")

    search_button.click()
    time.sleep(3)
    return

browser = webdriver.Chrome(path)
browser.get(url)
time.sleep(2)

try:
    search()
except:
    print("서울 검색 실패")

try:
    browser.find_element_by_xpath("//div[@id='filter_hoteltype']/div[2]/a[1]").click()
    time.sleep(3)
except:
    print("인기 필터 검색 실패")

try:
    browser.find_element_by_xpath("//div[@id='sort_by']/ul/li[4]/a").click()
    time.sleep(3)
except:
    print("요금 순 실패")

columns_name = ["HotelName", "HotelAddress", "HotelRating",
                "ReviewDate", "ReviewTitle", "ReviewRating", "Positive", "Negative"]
file = open(f'Booking.csv', 'w', encoding='utf-8')
writer = csv.writer(file)
writer.writerow(columns_name)

while True:
    try:
        hotel_links = browser.find_elements_by_class_name("sr_item_photo_link")
    except:
        print("호텔 링크 찾기 실패")
        break
    for link in hotel_links:
        link.send_keys(Keys.ENTER)
        time.sleep(2)
        browser.switch_to_window(browser.window_handles[-1])
        time.sleep(2)
        HotelName = browser.find_element_by_id("hp_hotel_name").text
        try:
            HotelAddress = browser.find_element_by_class_name(
                "hp_address_subtitle").text
        except:
            HotelAddress = None
        try:
            HotelRating = browser.find_element_by_class_name(
                "bui-review-score__badge").text
        except:
            HotelRating = None
        try:
            review_link = browser.find_element_by_id("show_reviews_tab")
            review_link.click()
            time.sleep(2)
        except:
            print("리뷰 없음")
            browser.close()
            browser.switch_to_window(browser.window_handles[0])
            time.sleep(2)
            continue
        try:
            browser.find_element_by_xpath(
                "//div[@id='review_lang_filter']/button[@class='bui-button bui-button--secondary']").click()
            time.sleep(2)
            browser.find_element_by_xpath(
                "//div[@class='bui-dropdown__content']/div/ul/li[2]/button[@data-value='ko']").click()
            time.sleep(2)
        except:
            print("한국어 리뷰 없음")
            browser.close()
            browser.switch_to_window(browser.window_handles[0])
            time.sleep(2)
            continue
        # idx = len(browser.find_elements_by_xpath(
        #     "//div[@class='bui-pagination__list page_link']/div[@class='bui-pagination__pages']/div/div"))
        # last_page = browser.find_element_by_xpath(
        #     f"//div[@class='bui-pagination__list page_link']/div[@class='bui-pagination__pages']/div/div[{idx}]/a/span[1]").text
        reviews = [[] for _ in range(5)]
        while True:
            columns = [browser.find_elements_by_xpath("//div[@class='bui-list__body']/span"),  # ReviewDate
                       browser.find_elements_by_xpath(
                "//div[@class='c-review-block__row']/div[@class='bui-grid']/div[1]/h3"),  # ReviewTitle
                browser.find_elements_by_xpath(
                "//div[@class='c-review-block__row']/div[@class='bui-grid']/div[2]/div/div"),  # ReviewRating
                browser.find_elements_by_xpath(
                "//div[@class='c-review-block__row']/div[@class='c-review']/div[@class='c-review__row']/p/span[3]"),  # Positive
                browser.find_elements_by_xpath(
                "//div[@class='c-review-block__row']/div[@class='c-review']/div[@class='c-review__row lalala']/p/span[3]")  # Negative
            ]
            for idx, column in enumerate(columns):
                for record in column:
                    if idx == 0:
                        data = record.text
                        year = data[:4]
                        month = data[6:-1]
                        reviews[idx].append(year + "-" + month)
                    else:
                        reviews[idx].append(record.text)
            try:
                review_next_btn = browser.find_element_by_xpath(
                    "//div[@class='bui-pagination__item bui-pagination__next-arrow']/a")
                review_next_btn.click()
                time.sleep(2)
            except:
                print("해당 호텔 리뷰 끝")
                break
        reviews = list(map(list, zip(*reviews)))
        hotel_info = [HotelName, HotelAddress, HotelRating]
        for review in reviews:
            writer.writerow(hotel_info + review)
        browser.close()
        browser.switch_to_window(browser.window_handles[0])
        time.sleep(2)
    try:
        hotel_next_btn = browser.find_element_by_xpath(
            "//nav[@class='bui-pagination__nav']/ul/li[3]/a")
        hotel_next_btn.click()
        time.sleep(4)
    except:
        print("페이지 끝")
        break
browser.quit()
