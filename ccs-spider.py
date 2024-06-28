#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File: 2
# @Author: Sesla
# @Time: 2024.02.27 16:57
# @Software: PyCharm

import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from lxml import etree

class ACM:
    def __init__(self, search_url):
        self.url = search_url.split('/')
        self.base_url = self.url[-1] or self.url[-2]
        self.pdf_url = f'https://{self.base_url}/doi/pdf/'
        self.headers = {
            'authority': self.base_url,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': f'https://{self.base_url}/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        }

    def rename(self, name):
        name = name.replace('\\', ' ')
        name = name.replace('/', ' ')
        name = name.replace(':', ' ')
        name = name.replace('*', ' ')
        name = name.replace('?', ' ')
        name = name.replace('"', ' ')
        name = name.replace('>', ' ')
        name = name.replace('<', ' ')
        name = name.replace('|', ' ')
        return name

    def get_search(self, keyword):
        params = {
            'AllField': keyword,
        }
        response = requests.get(
            f'https://{self.base_url}/action/doSearch',
            params=params,
            headers=self.headers,
            verify=False
        )
        html = etree.HTML(response.text)
        a = html.xpath('//li[@class="search__item issue-item-container"]//a')[0]
        self.name = ''.join(a.xpath('.//text()'))
        self.name = self.rename(self.name)
        self.href = f'https://{self.base_url}' + a.xpath('./@href')[0]
        print(self.name)
        print(self.href)

    def get_pdf(self):
        headers = {
            'authority': self.base_url,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': f'https://{self.base_url}/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        }
        response = requests.get(self.href, headers=headers, verify=False)
        html = etree.HTML(response.text)
        div = html.xpath('//div[@class="accordion sections"]/div/div')
        for i in div:
            name = i.xpath('./a/text()')[0]
            print(name)
            pdf_list = i.xpath('./div/label/input[2]/@value')[0].split(',')
            self.save_pdf(name, pdf_list)

    def save_pdf(self, name, pdf_list):
        path = self.name + '/' + self.rename(name)
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            print(f'{path} 已存在')
        for url in pdf_list:
            new_url = self.pdf_url + url
            print('-' * 30)
            print(new_url)
            print(f'{url} 下载中...')
            response = requests.get(new_url, headers=self.headers, verify=False)
            pdf_name = url.split('.')[-1]
            with open(f'./{path}/{pdf_name}.pdf', 'wb') as f:
                f.write(response.content)
            print(f'{url} 下载完成...')

    def run(self, url):
        self.get_search(url)
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        else:
            print(f'{self.name} 已存在')
        self.get_pdf()


if __name__ == '__main__':
    search_url = ''
    # 校园vpn登录后的url
    acm = ACM(search_url)
    # keyword = "CCS '21: Proceedings of the 2021 ACM SIGSAC Conference on Computer and Communications Security"
    keyword = "CCS '22: Proceedings of the 2022 ACM SIGSAC Conference on Computer and Communications Security"
    # keyword = "CCS '23: Proceedings of the 2023 ACM SIGSAC Conference on Computer and Communications Security"
    acm.run(keyword)