

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

        # 많은 시간이 지연되서 팝업이 뜰 수도 있기 때문에
        if hp_idx % 3 == 0:
            driver.refresh()
            time.sleep(7)
            print("refresh")

        hotel_pages = driver.find_elements_by_css_selector('a.review_count')
        if hotel_pages[hp_idx].get_attribute('class') == "review_count":
            hotel_pages[hp_idx].send_keys(Keys.ENTER)
            time.sleep(5)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(1)

            # review가 있는 hotel page에서 review 가져오기 시작
            tmp = get_hotel_review(driver)
            try:
                if len(tmp[0]) > 1 :
                    hotels_review_list += tmp
            except:
                pass
            print("hotel fin")
            driver.switch_to.window(driver.window_handles[0])

    click_hotel_next_btn(driver)

    df = pd.DataFrame(hotels_review_list)
    df.to_csv(f'../csv_output/Tripadvisor{page_idx}.csv',
              index=False,
              header=["HotelName", "HotelAddress", "HotelRating", "ReviewDate", "ReviewRating", "ReviewTitle",
                      "ReviewText"])

    print(f"csv {page_idx} finished")

    page_idx += 1
    break

driver.close()