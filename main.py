'''
Author: SN-Grotesque（sngrotesque，栀子鱼鱼花）
Date: 2026/06/24 08:18

这是我在精神极度萎靡+22小时未睡觉的情况下写的代码，你觉得屎的话那就是你对。
'''
from bs4 import BeautifulSoup
import requests
import json

def write_json(path :str, data :dict):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))

def parse_html(html_data :str):
    # 初始化对象
    artwork_list = {'data': [], 'next_page': None}
    soup = BeautifulSoup(html_data, 'lxml')

    # 找标签：标题
    artwork_title_path = 'html > body > div.ido > form#favform > table.itg.gltc > tr > td.gl3c.glname > a > div.glink'
    artwork_title = [x.text for x in soup.select(artwork_title_path)]
    # 找标签：链接
    artwork_url_path = 'html > body > div.ido > form#favform > table.itg.gltc > tr > td.gl3c.glname a'
    artwork_url = [x.get('href') for x in soup.select(artwork_url_path)]
    # 找标签：下一页
    next_page_path = 'html > body > div.ido > div.searchnav > div > a#dnext'
    next_page = soup.select_one(next_page_path)
    artwork_list['next_page'] = next_page.get('href') if next_page else None

    for i in range(len(artwork_title)):
        artwork_list['data'].append({'url': artwork_url[i], 'title': artwork_title[i]})

    return artwork_list

def parse_html_find_favorites_name(html_data :str):
    soup = BeautifulSoup(html_data, 'lxml')

    # 找标签：收藏夹名字
    favorites_name_page = 'html > body > div.ido > div.nosel > div.fp.fps > div'
    favorites_name = soup.select(favorites_name_page)[2].text

    return favorites_name

def fatch(cookie :str, proxy :str = 'http://127.0.0.1:1080'):
    def req(url :str, headers :dict, proxies :dict):
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        return response.text

    # 配置区
    headers = {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0'
    }
    proxies = {
        'http': proxy,
        'https': proxy
    }
    # 结果区
    result = {}

    for i in range(10):
        print(f'第 [{i : <2d}] 个分类。')
        url = f'https://e-hentai.org/favorites.php?favcat={i}' # 从第一个分类开始，如果不需要分类请直接去掉Query语句并去掉循环
        temp = []

        html = req(url, headers, proxies)
        artwork_list = parse_html(html)
        next_page_url = artwork_list['next_page']

        temp.extend(artwork_list['data'])

        while next_page_url:
            html = req(next_page_url, headers, proxies)
            artwork_list = parse_html(html)
            next_page_url = artwork_list['next_page']

            temp.extend(artwork_list['data'])

        result[f'favorites_{i}'] = {
            'count': len(temp),
            'name': parse_html_find_favorites_name(html),
            'data': temp
        }

    return result

def main():
    with open('./e-hentai.cookie', 'r', encoding='utf-8') as f:
        cookie = f.read().strip().replace('\r\n', '').replace('\n', '')

    res = fatch(cookie)
    write_json('./e-hentai.json', res)

if __name__ == '__main__':
    main()
