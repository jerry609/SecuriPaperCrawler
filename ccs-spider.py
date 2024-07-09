#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File: acm_downloader.py
# @Author: Sesla
# @Time: 2024.02.27 16:57
# @Software: PyCharm

import os
import urllib3
import requests
from lxml import etree
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ACMDownloader:
    def __init__(self, search_url):
        self.base_url = self._extract_base_url(search_url)
        self.pdf_url = f'https://{self.base_url}/doi/pdf/'
        self.headers = self._get_default_headers()

    def _extract_base_url(self, search_url):
        url_parts = search_url.split('/')
        return url_parts[-1] or url_parts[-2]

    def _get_default_headers(self):
        return {
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

    @staticmethod
    def sanitize_filename(name):
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '>', '<', '|']
        for char in invalid_chars:
            name = name.replace(char, ' ')
        return name

    def search(self, keyword):
        params = {'AllField': keyword}
        response = requests.get(
            f'https://{self.base_url}/action/doSearch',
            params=params,
            headers=self.headers,
            verify=False
        )
        html = etree.HTML(response.text)
        a = html.xpath('//li[@class="search__item issue-item-container"]//a')[0]
        self.name = self.sanitize_filename(''.join(a.xpath('.//text()')))
        self.href = f'https://{self.base_url}' + a.xpath('./@href')[0]
        print(f"Found: {self.name}")
        print(f"URL: {self.href}")

    def download_pdfs(self):
        response = requests.get(self.href, headers=self.headers, verify=False)
        html = etree.HTML(response.text)
        sections = html.xpath('//div[@class="accordion sections"]/div/div')
        for section in sections:
            section_name = section.xpath('./a/text()')[0]
            print(f"Downloading section: {section_name}")
            pdf_list = section.xpath('./div/label/input[2]/@value')[0].split(',')
            self._save_pdfs(section_name, pdf_list)

    def _save_pdfs(self, section_name, pdf_list):
        path = os.path.join(self.name, self.sanitize_filename(section_name))
        os.makedirs(path, exist_ok=True)
        for url in pdf_list:
            pdf_url = self.pdf_url + url
            print(f"Downloading: {pdf_url}")
            response = requests.get(pdf_url, headers=self.headers, verify=False)
            pdf_filename = f"{url.split('.')[-1]}.pdf"
            with open(os.path.join(path, pdf_filename), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {pdf_filename}")

    def run(self, year):
        keyword = f"CCS '{year}: Proceedings of the {year} ACM SIGSAC Conference on Computer and Communications Security"
        print(f"Searching for: {keyword}")
        self.search(keyword)
        os.makedirs(self.name, exist_ok=True)
        self.download_pdfs()

def main():
    parser = argparse.ArgumentParser(description="Download ACM CCS conference proceedings.")
    parser.add_argument("year", type=str, help="Year of the conference (e.g., '21, '22, '23)")
    parser.add_argument("--url", type=str, required=True, help="Base URL for ACM Digital Library (use your campus VPN URL)")
    args = parser.parse_args()

    acm_downloader = ACMDownloader(args.url)
    acm_downloader.run(args.year)

if __name__ == '__main__':
    main()
