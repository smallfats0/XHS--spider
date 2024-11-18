import os
import time
import requests
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from lxml import etree
import pandas as pd
from faker import Faker

# 初始化 Faker 用于生成随机请求头
fake = Faker()

# 使用 Faker 生成随机请求头
def get_random_headers():
    headers = {
        "User-Agent": fake.user_agent(),
        "X-Forwarded-For": fake.ipv4(),
        "Accept-Language": fake.language_code(),
    }
    return headers

# 读取代理池文件
with open('ip代理池.json', 'r', encoding='utf-8') as f:
    proxies = json.load(f)

# 随机选择代理
def get_random_proxy():
    return random.choice(proxies)

# 检查并关闭弹窗函数
def check_and_close_popup(driver):
    try:
        close_button_xpath = '//*[@id="app"]/div[1]/div/div[1]/div[1]/svg'
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, close_button_xpath))
        )
        driver.execute_script("arguments[0].click();", close_button)
        print("弹窗已关闭")
        time.sleep(5)  # 给页面更多时间加载
    except Exception:
        print("未找到弹窗或关闭按钮")

# 下拉到页面底部函数
def scroll_to_load(driver, n, items_per_scroll=8, delay=2):
    if n <= items_per_scroll:
        scroll_times = 1
    else:
        scroll_times = (n // items_per_scroll) + (1 if n % items_per_scroll != 0 else 0)

    for i in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"页面下拉 {i + 1}/{scroll_times} 次...")
        time.sleep(delay)

# 启动 Selenium WebDriver 并访问小红书探索页（增加代理支持）
def open_explore_page(driver, url, n):
    retries = 3
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(3)  # 等待页面加载完成
            check_and_close_popup(driver)
            scroll_to_load(driver, n)  # 动态下拉页面
            return
        except Exception:
            print(f"尝试打开探索页失败，重试 {attempt + 1}/{retries} 次...")

# 主程序
if __name__ == "__main__":
    # 设置 Edge 浏览器代理
    random_proxy = get_random_proxy()
    proxy_ip = random_proxy["http"].replace("http://", "")
    print(f"使用代理: {proxy_ip}")

    edge_options = Options()
    edge_options.add_argument(f"--proxy-server=http://{proxy_ip}")
    edge_options.add_argument("--headless")  # 无头模式
    edge_options.add_argument("--disable-gpu")

    # 初始化 WebDriver
    driver = webdriver.Edge(options=edge_options)

    # 示例 URL 和帖子数量
    url = "https://www.example.com"  # 替换为目标网址
    post_count = 20

    try:
        open_explore_page(driver, url, post_count)
        print("页面加载完成！")
    except Exception as e:
        print(f"页面加载失败: {e}")
    finally:
        driver.quit()
    
    # 使用 requests 测试代理
    try:
        random_proxy = get_random_proxy()
        proxy_dict = {"http": random_proxy["http"], "https": random_proxy["http"]}
        headers = get_random_headers()

        response = requests.get("https://httpbin.org/ip", headers=headers, proxies=proxy_dict, timeout=10)
        print("请求成功，返回内容:")
        print(response.json())
    except Exception as e:
        print(f"请求失败: {e}")