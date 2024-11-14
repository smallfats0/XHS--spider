import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import etree

# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

# 启动 Selenium WebDriver 并访问探索页
driver = webdriver.Chrome()
driver.get('https://www.xiaohongshu.com/explore')
time.sleep(5)  # 等待页面加载

# 尝试关闭弹窗（可选）
try:
    close_button_xpath = '//*[@id="app"]/div[1]/div/div[1]/div[1]/svg'
    close_button = driver.find_element(By.XPATH, close_button_xpath)
    driver.execute_script("arguments[0].click();", close_button)
    print("弹窗已关闭")
    time.sleep(2)
except Exception as e:
    print("未找到弹窗或关闭按钮:", e)

# 设置要获取的用户id
n = 10


# 打开 CSV 文件进行写入
with open('XHS.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['用户主页链接', '用户ID'])  # 写入表头

    # 遍历前 10 个主页链接进行测试
    for index in range(1, n + 1):
        home_link_xpath = f'//*[@id="exploreFeeds"]/section[{index}]/div/div/div/a'
        try:
            # 获取主页链接的 href 属性
            home_link = driver.find_element(By.XPATH, home_link_xpath)
            home_link_url = home_link.get_attribute("href")
            print(f"获取到主页链接: {home_link_url}")

            # 使用 requests 获取主页链接的内容
            response = requests.get(home_link_url, headers=headers)
            if response.status_code == 200:
                # 解析 HTML 内容
                user_page = etree.HTML(response.text)

                # 判断是否为广告
                ad_keywords = ["广告", "推广", "sponsored"]  # 自定义广告关键词
                page_text = ''.join(user_page.xpath('//text()'))  # 提取页面所有文本内容
                if any(keyword in page_text for keyword in ad_keywords):
                    print(f"跳过广告主页: {home_link_url}")
                    continue

                # 使用指定 XPath 提取用户 ID
                user_id_xpath = '//*[@id="userPageContainer"]/div[1]/div/div[2]/div[1]/div[1]/div[2]/div[2]/span[1]'
                user_id_element = user_page.xpath(user_id_xpath)
                if user_id_element:
                    user_id = user_id_element[0].text.strip()
                    print(f"获取到用户ID: {user_id}")
                    # 写入 CSV 文件
                    writer.writerow([home_link_url, user_id])
                else:
                    print("未找到用户ID，页面可能未完全加载。")
            else:
                print(f"请求失败，状态码: {response.status_code}")

            time.sleep(3)  # 每次请求后暂停 3 秒

        except Exception as e:
            print(f"处理第 {index} 个主页链接时出现错误: {e}")

# 关闭浏览器
driver.quit()

import pandas as pd
# 读取 CSV 文件
df = pd.read_csv('XHS.csv')

# 删除“用户主页链接”列
df = df.drop(columns=['用户主页链接'])

# 去重“用户ID”列
df = df.drop_duplicates(subset=['用户ID'])

# 保存去重后的结果到新文件
import pandas as pd

# 读取 CSV 文件
df = pd.read_csv('XHS_user_data.csv')

# 去重，仅保留用户ID列
df = df.drop_duplicates(subset=['用户ID'])[['用户ID']]

# 保存去重后的结果到 CSV 文件
df.to_csv('XHS_user_data.csv', index=False)
print("已去重并保存，仅保留用户ID。")

