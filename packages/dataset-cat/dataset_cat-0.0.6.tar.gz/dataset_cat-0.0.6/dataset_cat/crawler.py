"""Dataset crawler module for fetching images from various sources.

This module provides a unified interface for crawling images from different
anime image sources using the waifuc library.
"""

import logging
import os
from typing import Optional, Tuple

import requests

from dataset_cat.core.utils import ensure_directory, format_time_elapsed, setup_logging
from waifuc.source import (
    AnimePicturesSource,
    DanbooruSource,
    DerpibooruSource,
    DuitangSource,
    GelbooruSource,
    HypnoHubSource,
    KonachanNetSource,
    KonachanSource,
    LolibooruSource,
    PahealSource,
    PixivSearchSource,
    Rule34Source,
    SafebooruSource,
    WallHavenSource,
    YandeSource,
    ZerochanSource,
)
from waifuc.utils.download import download_file

# 数据源列表
SOURCE_LIST = [
    "Danbooru",
    "Zerochan",
    "Safebooru",
    "Gelbooru",
    "WallHaven",
    "Konachan",
    "KonachanNet",
    "Lolibooru",
    "Yande",
    "Rule34",
    "HypnoHub",
    "Paheal",
    "AnimePictures",
    "Duitang",
    "Pixiv",
    "Derpibooru",
]

logger = logging.getLogger(__name__)


class Crawler:
    @staticmethod
    def get_sources():
        return SOURCE_LIST  # 添加超时和重试逻辑

    @staticmethod
    def start_crawl(
        source_name: str, tags: str, limit: int, size: Optional[str], strict: bool
    ) -> Tuple[Optional[list], str]:
        proxies = {}
        if os.getenv("HTTP_PROXY"):
            proxies["http"] = os.getenv("HTTP_PROXY")
        if os.getenv("HTTPS_PROXY"):
            proxies["https"] = os.getenv("HTTPS_PROXY")

        session = requests.Session()
        session.proxies.update(proxies)

        # Size mapping for different sources
        def get_zerochan_select(size_param):
            """Map UI size options to Zerochan's valid select options"""
            # Handle legacy mapping for backward compatibility
            size_mapping = {
                "Original": "full",
                "Large": "large",
                "Medium": "medium",
                "Small": "medium",  # fallback to medium for small
            }
            # If already using correct values, return as-is
            if size_param in ["full", "large", "medium"]:
                return size_param
            # Otherwise use mapping
            return size_mapping.get(size_param, "large")  # default to 'large'

        source_mapping = {
            "Danbooru": lambda: DanbooruSource(tags=tags.split(","), min_size=limit),
            "Zerochan": lambda: ZerochanSource(tags, select=get_zerochan_select(size), strict=strict),
            "Safebooru": lambda: SafebooruSource(tags=tags.split(","), min_size=limit),
            "Gelbooru": lambda: GelbooruSource(tags=tags.split(","), min_size=limit),
            "WallHaven": lambda: WallHavenSource(
                query=tags, select=size if size in ["original", "thumbnail"] else "original"
            ),
            "Konachan": lambda: KonachanSource(tags=tags.split(","), min_size=limit),
            "KonachanNet": lambda: KonachanNetSource(tags=tags.split(","), min_size=limit),
            "Lolibooru": lambda: LolibooruSource(tags=tags.split(","), min_size=limit),
            "Yande": lambda: YandeSource(tags=tags.split(","), min_size=limit),
            "Rule34": lambda: Rule34Source(tags=tags.split(","), min_size=limit),
            "HypnoHub": lambda: HypnoHubSource(tags=tags.split(","), min_size=limit),
            "Paheal": lambda: PahealSource(tags=tags.split(",")),
            "AnimePictures": lambda: AnimePicturesSource(tags=tags.split(",")),
            "Duitang": lambda: DuitangSource(keyword=tags, strict=strict),
            "Pixiv": lambda: PixivSearchSource(query=tags, select=size),
            "Derpibooru": lambda: DerpibooruSource(tags=tags.split(","), select=size),
        }

        if source_name not in SOURCE_LIST:
            return None, f"Unsupported source: {source_name}"

        try:
            source_generator = source_mapping[source_name]()
            source = []
            for item in source_generator:
                source.append(item)
                if len(source) >= limit:
                    break
            return source, "Crawl task initialized."
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during crawling {source_name}: {e}", exc_info=True)
            return None, f"HTTP error during crawling {source_name}: {e}"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during crawling {source_name}: {e}", exc_info=True)
            return None, f"Connection error during crawling {source_name}: {e}"
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error during crawling {source_name}: {e}", exc_info=True)
            return None, f"Timeout error during crawling {source_name}: {e}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during crawling {source_name}: {e}", exc_info=True)
            return None, f"Network error during crawling {source_name}: {e}"
        except Exception as e:
            logger.error(f"Error during crawling {source_name}: {e}", exc_info=True)
            return None, f"Error during crawling {source_name}: {e}"

    @staticmethod
    def download_images(source: list, output_dir: str) -> str:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for item in source:
            url = item[1]  # Assuming the second element is the URL
            filename = os.path.join(output_dir, item[2]["filename"])  # Metadata contains the filename

            try:
                logger.info(f"Starting download: {url} -> {filename}")
                download_file(url, filename, desc=f"Downloading {filename}")
                logger.info(f"Successfully downloaded: {filename}")
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")

        return f"Images downloaded to {output_dir}"
