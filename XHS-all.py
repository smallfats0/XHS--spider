import time
import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
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

# 启动 Selenium WebDriver 并访问小红书探索页
driver = webdriver.Chrome()
explore_url = 'https://www.xiaohongshu.com/explore'
driver.get(explore_url)
time.sleep(5)  # 等待页面加载

# 尝试关闭弹窗（如果有）
try:
    close_button_xpath = '//*[@id="app"]/div[1]/div/div[1]/div[1]/svg'
    close_button = driver.find_element(By.XPATH, close_button_xpath)
    driver.execute_script("arguments[0].click();", close_button)
    print("弹窗已关闭")
    time.sleep(2)
except Exception as e:
    print("未找到弹窗或关闭按钮:", e)

# 设置要获取的帖子数
n = 1  # 这里设置成3个帖子用于测试，实际应用时可增加数量

# 打开 CSV 文件写入数据
with open('XHS_user_data.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['用户主页链接', '用户ID'])  # 写入表头

    # 遍历前 n 个帖子链接
    for index in range(1, n + 1):
        post_link_xpath = f'//*[@id="exploreFeeds"]/section[{index}]/div/a[2]'
        try:
            # 获取并点击每个帖子链接
            post_link = driver.find_element(By.XPATH, post_link_xpath)
            post_link_url = post_link.get_attribute("href")
            driver.get(post_link_url)
            print(f"进入帖子链接: {post_link_url}")
            time.sleep(3)  # 等待帖子页面加载

            # 模拟滚动以加载更多评论
            for _ in range(5):  # 根据需要调整滚动次数
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待内容加载

            # 等待评论区加载完成
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#noteContainer .comments-el'))
                )
            except Exception as e:
                print("评论区未加载完成:", e)
                continue

            # 获取加载完成的帖子页面源代码
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # 提取评论区中的所有用户链接
            comments_links = soup.select('#noteContainer .comments-el a')

            # 遍历每个用户主页链接
            for link in comments_links:
                user_home_url = link.get('href')
                if user_home_url and user_home_url.startswith("/user/profile"):
                    user_home_url = f'https://www.xiaohongshu.com{user_home_url}'
                    print(f"获取到用户主页链接: {user_home_url}")

                    # 使用随机请求头请求用户主页内容
                    headers = get_random_headers()
                    response = requests.get(user_home_url, headers=headers)
                    if response.status_code == 200:
                        user_page = etree.HTML(response.text)

                        # 使用指定 XPath 提取用户 ID
                        user_id_xpath = '//*[@id="userPageContainer"]/div[1]/div/div[2]/div[1]/div[1]/div[2]/div[2]/span[1]'
                        user_id_element = user_page.xpath(user_id_xpath)
                        if user_id_element:
                            user_id = user_id_element[0].text.strip()
                            print(f"获取到用户ID: {user_id}")
                            # 写入 CSV 文件
                            writer.writerow([user_home_url, user_id])
                        else:
                            print("未找到用户ID，页面可能未完全加载。")
                    else:
                        print(f"请求失败，状态码: {response.status_code}")

                    time.sleep(2)  # 每次请求后暂停 2 秒

            # 返回探索页
            driver.back()
            time.sleep(3)

        except Exception as e:
            print(f"处理第 {index} 个帖子链接时出现错误: {e}")

# 关闭浏览器
driver.quit()
import pandas as pd

# 读取 CSV 文件
df = pd.read_csv('XHS_user_data.csv')

# 去重，仅保留用户ID列
df = df.drop_duplicates(subset=['用户ID'])[['用户ID']]
df['用户ID'] = df['用户ID'].str.extract(r'小红书号：(.*)', expand=False)

# 保存去重后的结果到 CSV 文件
df.to_csv('XHS_user_data.csv', index=False)
print("用户数据已保存至 XHS_user_data.csv")