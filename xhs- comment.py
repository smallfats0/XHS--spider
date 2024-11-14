import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 启动 Selenium WebDriver
driver = webdriver.Chrome()
url = 'https://www.xiaohongshu.com/explore/67186b080000000021004729?xsec_token=ABVfZNwnipSb4LvNgqkk682dw8wIQULx4gwf7vaCYbc5I=&xsec_source=pc_feed'
driver.get(url)
time.sleep(5)  # 等待页面初次加载完成

# 模拟页面滚动以加载更多评论
for _ in range(5):  # 滚动多次，加载更多内容，根据需要调整次数
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # 等待内容加载

# 等待评论区加载完成
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#noteContainer > div.interaction-container > div.note-scroller > div.comments-el')))
except Exception as e:
    print("评论区未加载完成:", e)
    driver.quit()
    exit()

# 获取页面加载后的源代码
page_source = driver.page_source
driver.quit()

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(page_source, 'html.parser')

# 查找评论区中所有的 `<a>` 标签
comments_links = soup.select('#noteContainer .comments-el a')

# 遍历每个 `<a>` 标签，提取 href 和显示的文本
for index, link in enumerate(comments_links, start=1):
    link_href = link.get('href')
    link_text = link.get_text(strip=True)
    print(f"Link {index}:")
    print(f"Text: {link_text}")
    print(f"Href: {link_href}")
    print('-' * 40)