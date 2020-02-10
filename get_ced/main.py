
from __future__ import print_function

import os
import re
import tempfile

import shutil
import gzip
import pprint
import json
import time
import random
import ssl

from bs4 import BeautifulSoup

import utility
import settings

from html import parser as html_parser

import http.cookiejar

import urllib.request

COOKIE_FILE_PATH = os.path.join(settings.PICTURE_TEMP_PATH, "cookie.txt")

JPEG_COOKIE = "CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; _gid=GA1.2.845150499.1557673672; _ga=GA1.2.421634; _gat=1; CloudFront-Expires=1557843191; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3ODQzMTkxfX19XX0_; CloudFront-Signature=Rl0Wu82VvP1QEpL7hd%7ELhlanwmBlNTPIYodG6wn1NhJH3Ea-V2EaqMkM%7E93uw9%7EU-IkV6Qn3pUvrxgKJdYWHuEDKBu622%7ENwvUWd0jZg-t0VY23-8BAQLO6uLTLBh8L2aOAxe1bXgBQt3bfpgRKYEbY8sySQGK%7Eg5L2BChG%7E1bCNHuAYTqgqf-UBEZX4SBrDJXvwVsazmEvGk-%7Ez6a4y6iWuJ2Pvxh7A9LvGRKgOPR6rQ3bq6Zf4XI6nd8ml-5umo0gy6WKO9%7E7RcPfA68%7ED9sK02OSWZ1xXP51S6xEYIC9bUI1WRRcgu64szJiwtkmh3gjOq9-i27tEu7N10E0VWg__"


def execute_ffmpeg(url, output_file_path):

    if os.path.isfile(output_file_path):
        return

    utility.make_directory(output_file_path)

    command = (settings.FFMPEG_PATH, "-i", url,
               "-y",
               "-movflags", "faststart",
               "-c", "copy",
               "-bsf:a", "aac_adtstoasc",
               output_file_path)
    print(command)

    def call_back(returncode, stdout_message):
        print(returncode, stdout_message)
        pass

    utility.create_process(command, call_back, 1, 2400)()


def login_main(opener, token, prev_url):

    url_login = "/".join([settings.URL_ROOT, "mypage", "login"])
    print(url_login)

    post = {
        '_token': token,
        '_previous_url': prev_url,
        'email': settings.LOGIN_INFO["email"],
        'password': settings.LOGIN_INFO["password"],
    }

    print(post)

    req = urllib.request.Request(url_login, method='POST')
    req.add_header('Referer', settings.URL_ROOT)
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

    print(req.get_method())

    data = urllib.parse.urlencode(post).encode('utf-8')
    res = opener.open(req, data)
    res.close()


def get_opener(local_test_flag):

    if local_test_flag:
        return None

    cookie_jar = http.cookiejar.LWPCookieJar(COOKIE_FILE_PATH)
    cookie_jar.load()

    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(cookie_processor)

    # cookie_jar.save()

    return opener


def parse_json(file_path):

    print(file_path)

    with open(file_path, "r") as fp:
        json_dict = json.load(fp)

    pprint.pprint(json_dict)

    return json_dict


def get_iframe_html(opener, url, session_id):

    referer_url = settings.URL_ROOT

    req = urllib.request.Request(url)
    req.add_header('Referer', referer_url)
    req.add_header('accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

    res = opener.open(req)

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "{}_iframe.html".format(session_id))

    res_data = res.read()

    utility.make_directory(file_path)
    with open(file_path, mode="wb") as f:
        f.write(res_data)

    soup = BeautifulSoup(res_data, "html.parser")
    video_element = soup.find("video")
    if video_element is None:
        print("video element not found -> id:{}".format(session_id))
        return

    movie_url_element = video_element.find("source")
    if movie_url_element is None:
        print("video source element not found -> id:{}".format(session_id))
        return

    movie_url_value = movie_url_element.get("src")
    print(movie_url_value)

    parse_result = urllib.parse.urlparse(movie_url_value)
    scheme, netloc, url_path, _, _, _ = parse_result

    hd_2000k_url = url = urllib.parse.urlunparse((scheme, netloc, url_path.replace("index.m3u8", "hd_2000k_.m3u8"), None, None, None))

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "strage", "{}.mp4".format(session_id))

    execute_ffmpeg(hd_2000k_url, file_path)


def get_session_html(opener, url):

    referer_url = settings.URL_ROOT

    req = urllib.request.Request(url)
    req.add_header('Referer', referer_url)
    req.add_header('accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

    res = opener.open(req)

    session_id = url.split(r"/")[-1]

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "{}.html".format(session_id))

    res_data = res.read()

    utility.make_directory(file_path)
    with open(file_path, mode="wb") as f:
        f.write(res_data)

    soup = BeautifulSoup(res_data, "html.parser")

    iframe_url_element = soup.find("iframe", {"class": "frame embed-responsive-item"})
    if iframe_url_element is None:
        print("iframe not found -> id:{}".format(session_id))
        return

    iframe_url_value = iframe_url_element.get("src")

    # print(iframe_url_value)

    get_iframe_html(opener, iframe_url_value, session_id)


def get_login_page(opener):

    url_login = "/".join([settings.URL_ROOT, "mypage", "login"])
    print(url_login)

    req = urllib.request.Request(url_login)
    req.add_header('Referer', url_login)
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

    res = opener.open(req)

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "{}.html".format("login_page"))

    res_data = res.read()

    soup = BeautifulSoup(res_data, "html.parser")

    token_value_element = soup.find("input", {"name": "_token"})
    token_value = token_value_element.get("value")

    previous_url_element = soup.find("input", {"name": "_previous_url"})
    previous_url_value = previous_url_element.get("value")

    print(token_value, previous_url_value)

    return token_value, previous_url_value


def main():

    program_dict = parse_json(os.path.join(settings.PICTURE_TEMP_PATH, 'json_file.json'))

    for program_info in program_dict:
        print(program_info["URL"])

    local_test_flag = False

    opener = get_opener(local_test_flag)

    token, prev_url = get_login_page(opener)

    login_main(opener, token, prev_url)

    for program_info in program_dict:

        url = program_info["URL"]
        try:
            get_session_html(opener, url)
        except:
            print("pass -> ", url)
        # print(program_info)

    print("end")


if __name__ == "__main__":
    main()
