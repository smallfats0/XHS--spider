from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.edge.options import Options
import time
import json

# 设置 Edge 以无头模式运行
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

# 实例化浏览器
driver = webdriver.Edge(options=options)
# driver = webdriver.Edge()

ip_list = []
ip_port_dict = {}
proxies = []

a = 0
for i in range(1, 10):
    # 打开网页
    driver.get(f'https://www.kuaidaili.com/free/inha/{i}/')
    # 获取页面源代码
    html = driver.page_source
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html, 'lxml')

    all_l = soup.select('tbody>tr')

    for all_2 in all_l:
        # 确保tr标签内确实有td标签
        if len(all_2.select('td')) >= 2:
            a += 1
            ip_l = all_2.select('td')[0].text.strip()
            port_l = all_2.select('td')[1].text.strip()
            # 分别添加到列表和字典中
            ip_list.append(ip_l)
            ip_port_dict[ip_l] = port_l
            print(f'IP代理池正在加载第:{a}个')
            time.sleep(0.4)

print('IP代理池加载完成')

# 构建proxies列表
for ip in ip_list:
    proxies.append({'http': f'http://{ip}:{ip_port_dict[ip]}'})

# 写入JSON文件
with open('ip代理池.json', 'w', encoding='utf-8') as f:
    json.dump(proxies, f, ensure_ascii=False, indent=4)
    print("写入文件完成：ip代理池.json")

# 写入txt文件
with open('ip代理池.txt', 'w', encoding='UTF-8') as f:
    for i in proxies:
        f.write(str(i) + ',' + "\n")
    print("写入文件完成：ip代理池.txt")

driver.quit()
# time.sleep(999)
