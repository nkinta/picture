
from __future__ import print_function

import os
import re
import tempfile

import utility
import shutil
import gzip
import pprint
import json
import time
import random
import ssl
import change_time
from bs4 import BeautifulSoup

from PIL import Image

from html import parser as html_parser

import http.cookiejar

from get_pic_cheese import settings

import urllib.request

COOKIE_FILE_PATH = os.path.join(settings.PICTURE_TEMP_PATH, "cookie.txt")

JPEG_COOKIE = "CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; _gid=GA1.2.845150499.1557673672; _ga=GA1.2.421634; _gat=1; CloudFront-Expires=1557843191; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3ODQzMTkxfX19XX0_; CloudFront-Signature=Rl0Wu82VvP1QEpL7hd%7ELhlanwmBlNTPIYodG6wn1NhJH3Ea-V2EaqMkM%7E93uw9%7EU-IkV6Qn3pUvrxgKJdYWHuEDKBu622%7ENwvUWd0jZg-t0VY23-8BAQLO6uLTLBh8L2aOAxe1bXgBQt3bfpgRKYEbY8sySQGK%7Eg5L2BChG%7E1bCNHuAYTqgqf-UBEZX4SBrDJXvwVsazmEvGk-%7Ez6a4y6iWuJ2Pvxh7A9LvGRKgOPR6rQ3bq6Zf4XI6nd8ml-5umo0gy6WKO9%7E7RcPfA68%7ED9sK02OSWZ1xXP51S6xEYIC9bUI1WRRcgu64szJiwtkmh3gjOq9-i27tEu7N10E0VWg__"


def get_root_html(opener):

    req = urllib.request.Request(settings.URL_ROOT)
    req.add_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

    res = opener.open(req)

    root_html_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "root_html.html")
    with open(root_html_file_path, mode="wb") as f:
        f.write(res.read())

    with open(root_html_file_path, mode="r", encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    ethna_csrf_value = soup.find("input", {"name": "ethna_csrf"})["value"]

    return ethna_csrf_value


def login_main(opener, ethna_csrf_value):

    url_login = settings.URL_ROOT

    post = {
        'action_user_login': True,
        'ethna_csrf': ethna_csrf_value,
        'mailaddress': settings.LOGIN_INFO["mailaddress"],
        'passwd': settings.LOGIN_INFO["passwd"],
        'submit': '',
    }

    req = urllib.request.Request(url_login)
    req.add_header('Referer', settings.URL_ROOT)
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

    data = urllib.parse.urlencode(post).encode('utf-8')
    res = opener.open(req, data)
    res.close()


# @utility.try_again(3, 5.0)
def get_category_list(opener, eventno):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "event_{}.html".format(eventno))

    if not os.path.isfile(file_path):

        parse_result = urllib.parse.urlparse(settings.URL_ROOT)

        query_dict = {
            'action_user_FastViewer': 't',
            'eventno': eventno
        }

        scheme, netloc, path, params, _, fragment = parse_result
        query = urllib.parse.urlencode(query_dict)

        url = urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))

        req = urllib.request.Request(url)
        referer_url = settings.URL_ROOT
        req.add_header('Referer', referer_url)
        req.add_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
        req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
        req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

        res = opener.open(req)

        with open(file_path, mode="wb") as f:
            f.write(res.read())

    with open(file_path, mode="r", encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    category_no_tag_list = soup.find_all("li", {"class": "p-categoryList_category"})
    event_info = soup.find("span", {"class": "p-eventInfo_content"})

    date_kanji = event_info.text

    year_month_date = get_date(date_kanji)

    category_no_list = [category_no_tag["data-categoryno"] for category_no_tag in category_no_tag_list]

    """
    class CategoryParser(html_parser.HTMLParser):

        def handle_starttag(self, tag, attrs):  # 開始タグを扱うためのメソッド
            if tag == "li":
                attr_dict = dict(attrs)
                category_no = attr_dict.get("data-categoryno", None)
                if category_no:
                    category_no_list.append(category_no)

    parser = CategoryParser()

    with open(file_path, mode="r", encoding='utf-8') as f:
        parser.feed(str(f.read()))

    parser.close()
    """

    return category_no_list, year_month_date

"""
    class DateParser(html_parser.HTMLParser):

        def __init__(self):
            self.date_read_flag = False

        def handle_starttag(self, tag, attrs):  # 開始タグを扱うためのメソッド
            if tag == "span":
                attr_dict = dict(attrs)
                class_name = attr_dict.get("class", None)
                if class_name == "p-eventInfo_content":
                    self.date_read_flag = True

        def handle_data(self, data):
            if self.date_read_flag:
                print(data)
                self.date_read_flag = False

    date_parser = DateParser()

    with open(file_path, mode="r", encoding='utf-8') as f:
        date_parser.feed(str(f.read()))

    date_parser.close()
"""


@utility.try_again(3, 5.0)
def get_picture_list(opener, eventno, categoryno, offset=0):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "json_data", eventno, "category_picture_list_{}_{}.json".format(categoryno, offset))

    json_data = None
    if os.path.isfile(file_path):
        with open(file_path, mode="r") as f:
            try:
                json_data = json.loads(f.read())
            except:
                print("json read error ({})".format(file_path))

    if json_data is None:
        parse_result = urllib.parse.urlparse(settings.URL_ROOT)

        query_dict = {
            'action_Api_FastViewer_PhotoList': 'true',
            'eventno': eventno,
            'categoryno': categoryno,
            'offset': offset,
            'page': 'photolist',
            'sortkey': '0',
        }

        scheme, netloc, path, params, _, fragment = parse_result
        query = urllib.parse.urlencode(query_dict)

        url = urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))

        print(url)

        req = urllib.request.Request(url)
        referer_url = '{}/?action_user_FastViewer=t&eventno={}'.format(settings.URL_ROOT, eventno)
        req.add_header('Referer', referer_url)
        req.add_header('accept', 'application/json, text/javascript, */*; q=0.01')
        req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
        req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

        res = opener.open(req)

        utility.make_directory(file_path)
        with open(file_path, mode="wb") as f:
            f.write(res.read())

        with open(file_path, mode="r") as f:
            json_data = json.loads(f.read())

    json_data_list = []
    json_data_list.append(json_data)

    if json_data["message"]["pager"]["hasnext"]:
        next_json_data_list = get_picture_list(opener, eventno, categoryno, offset=offset + 100)
        json_data_list += next_json_data_list

    return json_data_list


@utility.try_again(3, 5.0)
def download_pic(opener, eventno, url, file_path):

    print("url-> ", url)
    print("file_path-> ", file_path)

    if opener is None:
        return

    req = urllib.request.Request(url)
    referer_url = '{}/?action_user_FastViewer=t&eventno={}'.format(settings.URL_ROOT, eventno)
    req.add_header('Referer', referer_url)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)
    req.add_header('accept-encoding', 'gzip, deflate, br')
    req.add_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
    req.add_header('cache-control', 'max-age=0')
    # req.add_header('cookie', JPEG_COOKIE)
    jpg = opener.open(req).read()

    utility.make_directory(file_path)
    with open(file_path, mode="wb") as f:
        f.write(jpg)


def combine_file(combine_file_path, pic_file_path_0, pic_file_path_1):

    def _get_mask_image(target_image_size):
        for ref_image_size in ((1200, 800), (1124, 800), (800, 1154), (800, 1200), (1116, 800), (1187, 800), (1167, 800)):
            if abs((target_image_size[0] / target_image_size[1]) - (ref_image_size[0] / ref_image_size[1])) < 0.02:
                mask_image = Image.open(os.path.join(settings.MASK_DIRECTORY_PATH, "mask_{}_{}.bmp".format(*ref_image_size))).convert("1").resize(target_image_size)
                return mask_image

        return None

    image_0 = Image.open(pic_file_path_0)
    image_1 = Image.open(pic_file_path_1)

    mask_image = _get_mask_image(image_0.size)

    print(pic_file_path_0, image_0.size)

    if (image_0.size == image_1.size == mask_image.size):
        out_image = Image.composite(image_1, image_0, mask_image)

        print(combine_file_path, out_image.size)
        utility.make_directory(combine_file_path)
        out_image.save(combine_file_path)

        # out_image.show()


def download_pics(opener, eventno, categoryno, offset, json_data, year_month_date):

    for pic_info in json_data["message"]["photos"]:

        url_data_list = [pic_info["m_pclogo1"], pic_info["m_pclogo2"]]
        sufix_list = ["1", "2"]
        year_month_date_num = [int(v) for v in year_month_date]
        cache_file_path_list = [os.path.join(settings.PICTURE_TEMP_PATH, "cache_pic_data", eventno, categoryno, str(offset), "{}_{}.jpg".format(pic_info["n"], s)) for s in sufix_list]
        # vsave_file_path_list = [os.path.join(settings.PICTURE_TEMP_PATH, "pic_data", , categoryno, str(offset), "{}_{}.jpg".format(pic_info["n"], s)) for s in sufix_list]

        for url_data, cache_file_path in zip(url_data_list, cache_file_path_list):
            if not os.path.exists(cache_file_path):
                download_pic(opener, eventno, url_data, cache_file_path)

                time.sleep(random.random())

        combine_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "combine_data", "{}_{:04}_{:02}{:02}".format(eventno, *year_month_date_num), categoryno, str(offset), "{}.jpg".format(pic_info["n"]))

        combine_file(combine_file_path, cache_file_path_list[0], cache_file_path_list[1])

        override_date(combine_file_path, year_month_date)
        # utility.make_directory(save_file_path)
        # shutil.copy(cache_file_path, save_file_path)


def login(local_test_flag):

    if local_test_flag:
        return None

    cookie_jar = http.cookiejar.MozillaCookieJar(COOKIE_FILE_PATH)
    cookie_jar.load()

    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(cookie_processor)

    ethna_csrf_value = get_root_html(opener)

    login_main(opener, ethna_csrf_value)

    return opener

DATE_INDEX_DICT = {}


def get_date(date_kanji):

    prog = re.compile("(20[12][0-9])年([01]*[0-9])月([0-3]*[0-9])日")

    m = prog.match(date_kanji)
    if m:
        year = m.group(1)
        month = m.group(2)
        date = m.group(3)

    return (year, month, date)


def override_date(file_path, year_month_date):

    year, month, date = year_month_date

    key = "{}{}{}".format(year, month, date)

    if key not in DATE_INDEX_DICT:
        DATE_INDEX_DICT[key] = 0
    else:
        DATE_INDEX_DICT[key] += 1

    index = DATE_INDEX_DICT[key]

    hour = (int(index / (60 * 60)) % 24)
    minute = (int(index / 60) % 60)
    sec = index % 60

    print(hour, minute, sec)

    change_time.set_time(file_path, int(year), int(month), int(date), 12 + hour, minute, sec, 0)


def main():

    local_test_flag = False
    opener = login(local_test_flag)

    # eventno_list = ["284373", "284372", "284371", "284370", "284369", "284368", "284367", "284366", "284365", "284364", "284363", "284362", "280837", "275509", "275510", "265727"]
    # eventno_list = ["366855", "366854", "366850", "366848", "400437", "349309", "349306", "349307", "348752", "348753", "348751", "338942"]
    eventno_list = ["366857", "366861", "366863", "366864"]

    for eventno in eventno_list:
        categoryno_list, year_month_date = get_category_list(opener, eventno)

        for categoryno in categoryno_list:
            print(eventno, categoryno)
            json_data_list = get_picture_list(opener, eventno, categoryno)
            # pprint.pprint(json_data_list)
            for i, json_data in enumerate(json_data_list):
                download_pics(opener, eventno, categoryno, i * 100, json_data, year_month_date)

    print("end")


def read():

    file_path = "C:/Users/nkinta/Desktop/hi_cheese_temp/test.json"
    with open(file_path, mode="r") as f:
        json_data = json.loads(f.read())
        pprint.pprint(json_data)


def main3():

    url_login = 'https://8122.jp'

    cookie_file_path = "C:/Users/nkinta/Desktop/hi_cheese_temp/cookie.txt"
    cookie_jar = http.cookiejar.MozillaCookieJar(cookie_file_path)
    cookie_jar.load()

    # req = urllib.request.Request(url)
    # req.add_header('cookie', 'displaymode=pc; _ga=GA1.2.421634; CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; sortkey=0; persistent=6d45613883a286175503b5858e3d849e1fa2da65; SenSESSID=83c1eb6fb6f825b97b793270749b3521fd3f977485f98685931181927f3c7cab; _gid=GA1.2.998022097.1557153908; CloudFront-Expires=1557156615; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3MTU2NjE1fX19XX0_; CloudFront-Signature=fbu6wRX5qS8FyBSuZgNRVgHG-aEeLYMJM0SN8oP2wVQUQfWNf35MBpUznUAx5kqpiUS8m6A3KHp5%7EwKBA6vR%7EZ12a84w%7EilK32WI363EHnzNNzzF4p%7E4VbIZQBuzgQ0j0a6rTWfNZwRYFGazTKfPJyEnW9lc78DoZOlVhwiHB9G3zAh8fqyzZPegmgCdfUQmaco7QieyBzGM%7EQQKrHR1lxeUOpHH8tjzGW9tLcD8PmDF1l9W7kXiTkV65VNXhuxIfrT6Sa-jXhXUD6mNMnyaXLN2j4vH6nGrzcSRorkaF0GKZluT4tQQa5YN3m%7EIZBIBuILskXY-wbP42wTQoBVbSw__; _gat=1')

    # my_cookie1 = http.cookiejar.Cookie(path="", domain=".8122.jp", expires="Session", name="CloudFront-Key-Pair-Id", value="APKAJZ4XANN3SJSZ5TOA")
    # my_cookie2 = http.cookiejar.Cookie(path="", domain=".8122.jp", expires="Session", name="CloudFront-Policy", value="eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3MTYzMjU3fX19XX0_")
    # my_cookie3 = http.cookiejar.Cookie(path="", domain=".8122.jp", expires="Session", name="CloudFront-Signature", value="Vcr3mF2WkCiSwmGIW-1aiitKh9FJ0LU5Fc3v1peSaXJj%7EZtLxgSDTb7AthRtmBpw-kCefmS5E8asds6vz4VxSzV79yHxcftPXDZRg8Kgiqb0FNKff3UMSH6GNZ6BFZZyTOq66NZdsKG9UFq9InjcarurKn5jIT16G9yGyD%7EkbpEJ7Otb-j889INl%7E3tyXNd0Cqi48mrmgplcV9RZLpa-Xvc78K1xTv7tH7ZjZ-uPWebUS4XRrFeYpmZg9RzN6t98fjSNZJVxJHldrTMp4VYliXo%7Ek2OsPxQVphLXxvXrTLlf6eSnqVAnlv90HUceRE0WfQ3Q0Xdzzwr0s0f6aNpXpQ__")
    # my_cookie4 = http.cookiejar.Cookie(path="", domain=".8122.jp", expires="Session", name="CloudFront-Expires", value="1557163257")

    # cookie_jar.set_cookie('_ga=GA1.2.421634; CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; _gid=GA1.2.998022097.1557153908; CloudFront-Expires=1557156615; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3MTU2NjE1fX19XX0_; CloudFront-Signature=fbu6wRX5qS8FyBSuZgNRVgHG-aEeLYMJM0SN8oP2wVQUQfWNf35MBpUznUAx5kqpiUS8m6A3KHp5%7EwKBA6vR%7EZ12a84w%7EilK32WI363EHnzNNzzF4p%7E4VbIZQBuzgQ0j0a6rTWfNZwRYFGazTKfPJyEnW9lc78DoZOlVhwiHB9G3zAh8fqyzZPegmgCdfUQmaco7QieyBzGM%7EQQKrHR1lxeUOpHH8tjzGW9tLcD8PmDF1l9W7kXiTkV65VNXhuxIfrT6Sa-jXhXUD6mNMnyaXLN2j4vH6nGrzcSRorkaF0GKZluT4tQQa5YN3m%7EIZBIBuILskXY-wbP42wTQoBVbSw__')
    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(cookie_processor)

    url_login = 'https://8122.jp'

    # ログインに使う送信データを作ります
    post = {
        'action_user_login': True,
        'mailaddress': 'maki.beniko.midoriko@gmail.com',
        'passwd': '1420061',
        'submit': '',
    }
    data = urllib.parse.urlencode(post).encode('utf-8')
    req = urllib.request.Request(url_login)
    req.add_header('Referer', 'https://8122.jp')
    req.add_header('accept-language', 'ja,en-US;q=0.9,en;q=0.8')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36')

    res = opener.open(req, data)
    cookie_jar.save()
    print(res.info())
    res.close()

    # req = urllib.request.Request(url_login)
    # json = opener.open(req)

    url = 'https://8122.jp/?action_Api_FastViewer_PhotoList=true&eventno=284372&categoryno=2041893&offset=0&page=photolist&sortkey=0&_=1557322114885'

    req = urllib.request.Request(url)
    req.add_header('Referer', 'https://8122.jp/?action_user_FastViewer=t&eventno=284372')
    req.add_header('accept', 'application/json, text/javascript, */*; q=0.01')
    # req.add_header('accept-encoding', 'gzip, deflate, br')
    req.add_header('accept-language', 'ja,en-US;q=0.9,en;q=0.8')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36')
    # req.add_header('cookie', 'displaymode=pc; CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; sortkey=0; persistent=6d45613883a286175503b5858e3d849e1fa2da65; _gid=GA1.2.1497753385.1557243028; _ga=GA1.2.421634; SenSESSID=f6111d364fe9b63307db3c6b5faf1f469127d092d1e6226334a4a4cd2cb5a583; CloudFront-Expires=1557327534; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3MzI3NTM0fX19XX0_; CloudFront-Signature=GL59feJU67eZeoZ16WUYAvquaIEs2XG7ECyT5vJx1OM-O9mxSS%7E6eN2a8X%7ESXMdyR8acr6ng06VpSGVdh3hyJb%7EhICJI1iftjv0h8RusppQ8EbwgXe2%7EOwfBalB5UWyfLQJAm4ZeeNI2E5XfevAObV-lXRDkhxKmihA6XQ1SEJeduAYeC8cCPbH3FibnHYSb6DMBcxIzFj58wq%7Efa54ybMsshP03o%7EBw4sMSBlBEKAmm%7EKqYStglSt-U37qXwA-iYkBir51gtR5T22TmtuGyS3t-m080xXFFokxIwsgVc22bnGeKZC%7EyQFg9vq7itBHh9W1vSoWJ1yzPE2lAoq-y1w__; _gat=1')
    # jpg = urllib.request.urlopen(url).read()
    res2 = opener.open(req)

    file_path = "C:/Users/nkinta/Desktop/hi_cheese_temp/test.json"

    with open(file_path, mode="wb") as f:
        f.write(res2.read())
        # sf = StringIO.StringIO(res2.read())
        # pprint.pprint(res2.read())

    """
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
    """


def main2():

    # url = 'https://cdn.shopify.com/s/files/1/0864/2280/products/vegusto_classic_blue__51314.jpeg'
    url = "https://cdn.image.8122.jp/v1/w=1200,h=800,logo=8122logo2_380x.png,lr=600:300:300,lp=nw:-290:-70/8122jp/stg01/photoORG/conv_20190315ebara_284373/01/01/00700-2887.JPG?signature=06a9b81c17016dd9eac2332e0e75ee95fa0fde36875ec8039f05c3c2a3effea6&updatedday=20190322102814"
    url2 = "https://cdn.image.8122.jp/v1/w=1200,h=800,logo=8122logo2_380x.png,lr=600:300:300,lp=nw:-290:-70,tr=0.035/8122jp/stg01/photoORG/conv_20190315ebara_284373/02/01/00908-2887.JPG?signature=21f3f686b0ddcf7ce9cf6a01f80448899d0a327f5e3ece60093266154598496b&updatedday=20190322102816"

    req = urllib.request.Request(url)
    req.add_header('Referer', 'https://8122.jp/?action_user_FastViewer=t&eventno=284373')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36')
    req.add_header('cookie', 'CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; _gid=GA1.2.845150499.1557673672; _ga=GA1.2.421634; CloudFront-Expires=1557759992; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3NzU5OTkyfX19XX0_; CloudFront-Signature=RNDSXV9Y1QhSWnM5fyzs0uxNvtr14A4SVAB3dG1Q0UYzAB%7EQ6vO1Zq2c7ACGNueEcjvo3bdTVHn7UsPvhexWncBoJ3rYExAOHZZ4-MCh73Qz42%7Ec1RCuameG7AONCbA2vh6Zat9xqk6sPPgGyXWBp7TCXMmpAEWg9YmJ3lXwCIAaR0rUsyqGKbU-FQ2Qil9iN0Dm1r4XWajnF8MATAU0v1rArk-TNGyVQGSj22%7E9qF96GBxNXr1C4FFmbg8zOzZXpUoV2aHRk0sxBzQkFtfnxEtL5FWkPIuf2UMSbRN6rV2hAdOIifcJFHDnDfTARnwew7Se41vgXtl-9X99aGUPnQ__')
    # jpg = urllib.request.urlopen(url).read()
    jpg = urllib.request.urlopen(req).read()

    file_path = "C:/Users/nkinta/Desktop/hi_cheese_temp/test.jpg"

    with open(file_path, mode="wb") as f:
        f.write(jpg)
        print("saved")

    """
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
        print(body)
    """


if __name__ == "__main__":
    main()
