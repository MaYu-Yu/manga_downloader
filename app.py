import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import json

logging.basicConfig(level=logging.ERROR)

# 指定ChromeDriver.exe的路徑
chrome_path = "./chromedriver.exe"

# 設置ChromeDriver的選項
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# 啟動ChromeDriver
service = Service(chrome_path)
service.start()
driver = webdriver.Remote(service.service_url, options=chrome_options)

# 用戶輸入要搜索的關鍵字
search_keyword = input("請輸入要搜索的關鍵字：")

# 目標網址
url = "https://www.cartoonmad.com/"

try:
    # 使用ChromeDriver打開網頁
    driver.get(url)

    # 找到搜尋框並輸入關鍵字
    search_input = driver.find_element(By.NAME, "keyword")
    search_input.send_keys(search_keyword)

    # 找到提交按鈕並點擊submit
    submit_button = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/table/tbody/tr[3]/td/input')
    submit_button.click()

    # 等待搜索結果頁面加載完成
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/table')))

    # 獲取搜索結果中的超連結和對應的標題
    search_results = driver.find_elements(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/table//a')
    result_links = {} # title:link
    for result in search_results:
        title = result.text
        err_title_patterns = [
            r"更新到第 ",
            r"^\s*$"       # Is entirely empty or contains only whitespace
        ]
        if any(re.search(pattern, title) for pattern in err_title_patterns): continue
        link = result.get_attribute("href")
        result_links[title] = link
        
    # 輸出搜索結果
    print("搜索結果：")
    for i, (title, link) in enumerate(result_links.items(), start=1):
        print(f"{i}. {title}: {link}")

    # 讓用戶選擇一個結果
    choice = int(input("請選擇一個結果編號："))
    selected_title = list(result_links.keys())[choice - 1]
    selected_link = result_links[selected_title]

    # 打開用戶選擇的漫畫鏈接
    driver.get(selected_link)

    # 等待頁面加載完成
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/table[3]/tbody/tr/td/fieldset/table')))

    # 獲取漫畫集數和每集的鏈接及頁數
    chapter = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[1]/td[2]/table/tbody/tr[4]/td/table/tbody/tr[2]/td[2]/table[3]/tbody/tr/td/fieldset/table')
    chapter_info = []
    link_elements = chapter.find_elements(By.TAG_NAME, 'a')
    for link_element in link_elements:
        chapter_title = link_element.text
        chapter_link = link_element.get_attribute('href')
        pages = chapter.find_element(By.TAG_NAME, 'font').text
        chapter_info.append({
            'title': chapter_title,
            'link': chapter_link,
            'pages': pages
        })

    # 將漫畫信息存儲到JSON文件中
    output_filename = f"{selected_title}.json"
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(chapter_info, json_file, ensure_ascii=False, indent=4)

    print(f"漫畫信息已儲存到 {output_filename}")

except Exception as e:
    print(e)

finally:
    # 關閉瀏覽器
    driver.quit()
