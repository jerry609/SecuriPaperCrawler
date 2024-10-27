# securipaperbot/utils/downloader.py

from typing import Dict, List, Any, Optional
import aiohttp
import asyncio
from pathlib import Path
import urllib.parse
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from ..utils.logger import setup_logger


class PaperDownloader:
    """论文下载工具类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = setup_logger(__name__)
        self.download_path = Path(self.config.get('download_path', './papers'))
        self.download_path.mkdir(parents=True, exist_ok=True)

        # 配置下载重试参数
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 5)

        # 配置并发限制
        self.semaphore = asyncio.Semaphore(self.config.get('max_concurrent_downloads', 5))

        # 会议URL模板
        self.conference_urls = {
            'ccs': 'https://dl.acm.org/doi/proceedings/10.1145/',
            'sp': 'https://ieeexplore.ieee.org/xpl/conhome/',
            'ndss': 'https://www.ndss-symposium.org/',
            'usenix': 'https://www.usenix.org/conference/'
        }

    async def download_paper(self, url: str, title: str) -> Dict[str, Any]:
        """下载单篇论文"""
        async with self.semaphore:
            try:
                # 生成文件名
                safe_title = self._sanitize_filename(title)
                file_path = self.download_path / f"{safe_title}.pdf"

                # 检查是否已下载
                if file_path.exists():
                    self.logger.info(f"Paper already exists: {title}")
                    return {
                        'success': True,
                        'path': str(file_path),
                        'cached': True
                    }

                # 下载论文
                content = await self._download_with_retry(url)
                if content:
                    # 保存文件
                    file_path.write_bytes(content)

                    return {
                        'success': True,
                        'path': str(file_path),
                        'cached': False
                    }
                else:
                    raise Exception("Failed to download paper")

            except Exception as e:
                self.logger.error(f"Error downloading paper {title}: {str(e)}")
                return {
                    'success': False,
                    'error': str(e)
                }

    async def get_conference_papers(self, conference: str, year: str) -> List[Dict[str, Any]]:
        """获取会议论文列表"""
        try:
            if conference not in self.conference_urls:
                raise ValueError(f"Unsupported conference: {conference}")

            base_url = self.conference_urls[conference]
            papers = []

            # 根据会议类型选择相应的解析方法
            if conference == 'ccs':
                papers = await self._parse_ccs_papers(base_url, year)
            elif conference == 'sp':
                papers = await self._parse_sp_papers(base_url, year)
            elif conference == 'ndss':
                papers = await self._parse_ndss_papers(base_url, year)
            elif conference == 'usenix':
                papers = await self._parse_usenix_papers(base_url, year)

            return papers

        except Exception as e:
            self.logger.error(f"Error getting papers for {conference} {year}: {str(e)}")
            raise

    async def _parse_ccs_papers(self, base_url: str, year: str) -> List[Dict[str, Any]]:
        """解析ACM CCS论文列表"""
        papers = []
        url = f"{base_url}ccs{year}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # 解析论文列表
                        for paper in soup.find_all('div', class_='paper'):
                            paper_info = {
                                'title': paper.find('h2').text.strip(),
                                'authors': [a.text.strip() for a in paper.find_all('a', class_='author')],
                                'abstract': paper.find('div', class_='abstract').text.strip(),
                                'url': paper.find('a', class_='pdf')['href'],
                                'doi': paper.get('data-doi', '')
                            }
                            papers.append(paper_info)
                    else:
                        raise Exception(f"Failed to fetch CCS papers: {response.status}")

            return papers

        except Exception as e:
            self.logger.error(f"Error parsing CCS papers: {str(e)}")
            raise

    async def _download_with_retry(self, url: str) -> Optional[bytes]:
        """带重试机制的下载"""
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.read()
                        else:
                            self.logger.warning(
                                f"Download failed (attempt {attempt + 1}/{self.max_retries}): "
                                f"HTTP {response.status}"
                            )

            except Exception as e:
                self.logger.warning(
                    f"Download error (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                )

            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        return None

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        # 移除不允许的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')

        # 将空格替换为下划线
        filename = filename.replace(' ', '_')

        # 限制长度
        max_length = 255 - len('.pdf')
        if len(filename) > max_length:
            filename = filename[:max_length]

        return filename.strip('._')

    async def cleanup_old_files(self, max_age_days: int = 30):
        """清理旧文件"""
        try:
            now = datetime.now()
            for file_path in self.download_path.glob('*.pdf'):
                file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                age_days = (now - file_age).days

                if age_days > max_age_days:
                    file_path.unlink()
                    self.logger.info(f"Removed old file: {file_path}")

        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {str(e)}")

    def validate_config(self) -> bool:
        """验证配置"""
        required_keys = ['download_path', 'max_retries', 'max_concurrent_downloads']
        return all(key in self.config for key in required_keys)