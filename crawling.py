import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import os
from github_funcs import *

def crawling_favorite_blogs(blog_info_lst, 
                            today = datetime.now().date() - timedelta(days=1)):
    """
    주어진 사이트 정보를 사용하여 각 사이트의 첫 페이지를 크롤링하고, 
    게시글의 발행 시간, 제목, 링크를 추출합니다.
    그 후 어제 날짜와 비교해 어제 날짜인 글만 추출합니다. 
    (매일 00시에 이 프로그램을 Github Action으로 돌릴 예정)

    매개변수:
    blog_info_lst (list): blog_tuple로 구성된 리스트.
    - blog_tuple (tuple): 블로그 이름과 blog_dict로 구성된 튜플
        - blog_name (str): 각 블로그의 이름(별명)
        - blog_dict (dict): 각 사이트의 구성 정보를 포함하는 사전. 
                            각 키는 블로그의 별칭이며, 
                            값은 다음 정보를 포함하는 사전입니다:
            - base_url (str): 사이트의 기본 URL.
            - post_path (str): 게시글이 나열된 페이지의 경로.
            - detail_page_is_absolute (boolean): 상세 페이지의 경로가 absolute로 
                                                연결 되어있는가에 대한 정보
            - datetime_format (str): 발행 시간의 날짜 형식을 지정하는 문자열.
            - post_info (list): 게시글 리스트를 가져오기 위한 정보를 포함하는 리스트
                                [태그, 검색 방법, class/id/name 값].
            - title_info (list): 게시글 제목을 찾기 위한 정보를 포함하는 리스트 
                                [태그, 검색 방법, class/id/name 값].
            - link_info (list): 게시글 링크를 찾기 위한 정보를 포함하는 리스트.
            - publish_info (list): 게시글의 발행 시간 정보를 찾기 위한 리스트.
            - need_enter_detail_page_for_publish_date (bool): 
                    게시 날짜 정보를 얻기 위해 상세 페이지에 접근해야 하는지 여부.

    today (datetime): 수집할 날짜를 지정하는 변수. 기본적으로 비워두지만, test시에는 
                    특정 날짜의 데이터를 가져올 수 있는지 체크 용도로 사용

    반환 값:
    crawling_result_lst (list): 크롤링 결과 중 타겟 날짜에 작성된 글 리스트
        - crawling_result_tuple (tuple): crawling_result_lst의 요소로 
                                        각 사이트의 이름과 각 사이트에서 추출한 
                                        정보를 담고 있음
            - name (str): 블로그 이름
            - data (list): 타겟 날짜에 맞는 포스트만 모은 정보들 
                            [링크, 제목, 게시 날짜]로 구성


    예제:
    blog_info = ("example_blog", {
                    "base_url": "https://example.com",
                    "post_path": "/posts",
                    "detail_page_is_absolute": False,
                    "datetime_format": "%Y-%m-%d",
                    "posts_info": ["div", "class", "post"],
                    "title_info": ["h1", "class", "post-title"],
                    "link_info": ["a", "name", "post-link"],
                    "publish_info": ["span", "class", "publish-date"],
                    "need_enter_detail_page_for_publish_date": False
                })
    blog_dict_list = [blog_info]
    crawling_favorite_blogs(blog_dict_list)
    """
    crawling_result_lst = []
    
    for blog_name, blog_dict in blog_info_lst:
        soup = bs(requests.get(blog_dict["base_url"] + blog_dict["post_path"]).text, "html.parser")
        posts_info = blog_dict["posts_info"]
        link_info = blog_dict["link_info"]
        title_info = blog_dict["title_info"]
        publish_info = blog_dict["publish_info"]
        posts = soup.find_all(posts_info[0], attrs={posts_info[1]:posts_info[2]})
        result_lst = []
        for post in posts:
            try:
                if link_info[0] == None:
                    # 리스트 자체가 a 태그인 경우...
                    link = post.get("href")
                elif link_info[1] == None:
                    link = post.find('a').get("href")
                else:
                    link = post.find(link_info[0], attrs={link_info[1]:link_info[2]}).get("href")

                if blog_dict["detail_page_is_absolute"] is not None and not blog_dict["detail_page_is_absolute"]:
                    link = blog_dict["base_url"] + link

                if title_info[1] == None:
                    title = post.find(title_info[0]).get_text()
                else:
                    title = post.find(title_info[0], attrs={title_info[1]:title_info[2]}).get_text()


                if blog_dict["need_enter_detail_page_for_publish_date"]:
                    detail_soup = bs(requests.get(link).text, "html.parser")
                    publish_date_str = detail_soup.find(publish_info[0], attrs={publish_info[1]:publish_info[2]}).get_text()
                else:
                    if publish_info[1] == None:
                        publish_date_str = post.find(publish_info[0]).get_text()
                    else:
                        publish_date_str = post.find(publish_info[0], attrs={publish_info[1]:publish_info[2]}).get_text()

                publish_date = datetime.strptime(publish_date_str, blog_dict["datetime_format"])
                if today == publish_date.date():
                    result_lst.append((link, title, publish_date))
            except:
                pass
            
        crawling_result_lst.append((blog_name, result_lst))
    return crawling_result_lst

def publish_git_issue(crawling_result_lst):
    """
    매개변수:
    crawling_result_lst (list): 크롤링한 결과 중 각 사이트별로 타겟 날짜인 포스트만 모은 리스트
        - crawling_result_tuple (tuple): crawling_result_lst의 요소로 각 사이트의 이름과 각 사이트에서 추출한 정보를 담고 있음
            - name (str): 블로그 이름
            - data (list): 타겟 날짜에 맞는 포스트만 모은 정보들 [링크, 제목, 게시 날짜]로 구성

    """
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
    REPO_NAME = "favorite-blog-crawling"
    repo = get_github_repo(GITHUB_TOKEN, REPO_NAME)
    total_new_post_blogs = 0
    body = "| 블로그 이름 | 제목 | 게시날짜 |\n" + "| - | - | - |\n"
    for blog_name, blog_posts in crawling_result_lst:
        if len(blog_posts) > 0:
            total_new_post_blogs += 1
            for post in blog_posts:
                body += f"| {blog_name} | [{post[1]}]({post[0]}) | {post[2]} |\n"
    
    if total_new_post_blogs > 0:
        title = f"{total_new_post_blogs}개의 블로그에서 새로운 포스트가 게시되었습니다."
        upload_github_issue(repo, title, body)




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
    crawling_result_lst = crawling_favorite_blogs(blog_infos)
    publish_git_issue(crawling_result_lst)