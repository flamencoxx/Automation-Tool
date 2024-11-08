import requests
from bs4 import BeautifulSoup


class TestAPI:
    def test1(self):
        print("Testing")

    def test2(self):
        # 目标URL
        url = 'https://www.reddit.com/r/golang/comments/18ujt6g/new_at_go_start_here/'

        # 发送GET请求
        response = requests.get(url)

        # 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取所有的<a>标签
        links = soup.find_all('a')

        # 遍历并打印链接
        for link in links:
            print(link.get('href'))

    def test3(self):
        print("Testing")
