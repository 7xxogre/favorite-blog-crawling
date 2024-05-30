from crawling import *
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import os

if __name__ == "__main__":
    blog_infos = [
        ("junia3", {
            "base_url": "https://junia3.github.io/blog",
            "post_path": "",
            "detail_page_is_absolute": None,
            "datetime_format": "%B %d, %Y",
            "posts_info": ["div", "name", "blogcards"],
            "title_info": ["h1", "class", "title is-size-4-touch"],
            "link_info": ["a", None, None],
            "publish_info": ["span", "class", "has-text-weight-semibold"],
            "need_enter_detail_page_for_publish_date": False
        }),
        ("firstpenguine", {
            "base_url": "https://blog.firstpenguine.school",
            "post_path": "/category",
            "detail_page_is_absolute": False,
            "datetime_format": "%Y. %m. %d. %H:%M",
            "posts_info": ["div", "class", "post-item"],
            "title_info": ["span", "class", "title"],
            "link_info": ["a", None, None],
            "publish_info": ["span", "class", "date"],
            "need_enter_detail_page_for_publish_date": True
        }),
        ("kciter", {
            "base_url": "https://kciter.so",
            "post_path": "",
            "detail_page_is_absolute": False,
            "datetime_format": "%Y-%m-%d",
            "posts_info": ["a", "class", "css-zhckuc e349bdu1"],
            "title_info": ["div", None, None],
            "link_info": [None, None, None],
            "publish_info": ["small", None, None],
            "need_enter_detail_page_for_publish_date": False
        }),
        ("parksb", {
            "base_url": "https://parksb.github.io/",
            "post_path": "articles.html",
            "detail_page_is_absolute": False,
            "datetime_format": "%Y.%m.%d",
            "posts_info": ["li", None, None],
            "title_info": ["span", "class", "heading"],
            "link_info": ["a", None, None],
            "publish_info": ["time", None, None],
            "need_enter_detail_page_for_publish_date": False
        })
    ]
    crawling_result_lst = crawling_favorite_blogs(blog_infos, datetime(2024, 1, 23).date())
    print(crawling_result_lst)