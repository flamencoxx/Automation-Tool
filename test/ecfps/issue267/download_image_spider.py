import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def download_image(url, folder):
    """下载图片到指定文件夹"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # 从URL中提取文件名
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")


def scrape_blog(base_url, blog_path):
    """爬取博客并下载图片"""
    full_url = urljoin(base_url, blog_path)
    response = requests.get(full_url)

    if response.status_code != 200:
        print(f"Failed to access {full_url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # 假设每个博客文章都有一个唯一的标题
    blog_title = soup.find('h1').text.strip()
    safe_title = "".join([c for c in blog_title if c.isalnum() or c in (' ', '-', '_')]).rstrip()

    # 创建以博客标题命名的文件夹
    folder_name = safe_title[:50]  # 限制文件夹名长度
    os.makedirs(folder_name, exist_ok=True)

    # 查找所有图片标签
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            full_img_url = urljoin(full_url, img_url)
            download_image(full_img_url, folder_name)


def main():
    base_url = "https://10.3.100.125"  # 替换为目标博客的基础URL
    blog_path = "/share/page/site/enterpriseconnect-fps/"  # 替换为博客文章列表的路径

    # 获取博客列表页面
    response = requests.get(urljoin(base_url, blog_path))
    soup = BeautifulSoup(response.text, 'html.parser')

    # 假设每个博客链接都在<a>标签中，并且有特定的class
    for link in soup.find_all('a', class_='blog-link'):  # 根据实际情况调整class名
        blog_url = link.get('href')
        if blog_url:
            scrape_blog(base_url, blog_url)


if __name__ == "__main__":
    main()
