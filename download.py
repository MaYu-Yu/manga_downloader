import os
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
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(level=logging.ERROR)

# 指定ChromeDriver.exe的路徑
chrome_path = "./chromedriver.exe"

# 設置ChromeDriver的選項
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--log-level=3') 

# 啟動ChromeDriver
service = Service(chrome_path)
service.start()
driver = webdriver.Remote(service.service_url, options=chrome_options)

# 設定儲存圖片的資料夾
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 讀取JSON檔案
json_file_path = input("請輸入JSON檔案的路徑：")
try:
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        chapter_info = json.load(json_file)
    chapter_name = os.path.splitext(os.path.basename(json_file_path))[0] # json名稱
    # 下載每個章節的圖片
    for chapter in chapter_info:
        chapter_title = chapter['title']
        chapter_link = chapter['link']
        chapter_pages = chapter['pages']
        
        # 目標網址
        url = chapter_link

        # 設定儲存圖片的資料夾
        output_folder = os.path.join("output", chapter_name, chapter_title)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        chapter_num = 0
        while True:
            chapter_num+=1
            # 使用ChromeDriver打開網頁
            driver.get(url)

            # 等待圖片加載完成
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img[src*=".jpg"]')))

            # 獲取第一張圖片元素
            image = driver.find_element(By.CSS_SELECTOR, 'img[src*=".jpg"]')

            # 獲取圖片URL
            image_src = image.get_attribute("src")

            # 儲存圖片，以連續順序命名
            image_path = os.path.join(output_folder, f"{chapter_name}_{chapter_title}_{chapter_num}.jpg")
            response = requests.get(image_src)
            with open(image_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"圖片 {image_path} 已儲存")

            try:
                # 找到下一頁按鈕
                next_button = driver.find_element(By.XPATH, '//a[@class="pages" and contains(text(), "下一頁")]')
            except NoSuchElementException:
                print("已到達最後一頁，結束下載。")
                break
            
            # 點擊下一頁按鈕
            next_button.click()
            # 等待頁面跳轉完成
            time.sleep(5)
            # 更新當前網址
            url = driver.current_url
            if "thend.asp" in url:
                print("已到達最後一頁，結束下載。")
                break
except Exception as e:
    print(e)

finally:
    # 關閉瀏覽器
    driver.quit()
