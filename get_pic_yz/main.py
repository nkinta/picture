
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

from PIL import Image, ImageOps, ImageEnhance

from html import parser as html_parser

import http.cookiejar

from get_pic_yz import settings

import urllib.request

import pyocr
pyocr.tesseract.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# pyocr.cuneiform.CUNEIFORM_CMD = r'C:\Users\nkinta\AppData\Local\Programs\Python\Python35\Lib\site-packages\pyocr\__pycache__\cuneiform.cpython-35.pyc'

COOKIE_FILE_PATH = os.path.join(settings.PICTURE_TEMP_PATH, "cookie.txt")

JPEG_COOKIE = "CloudFront-Key-Pair-Id=APKAJZ4XANN3SJSZ5TOA; _gid=GA1.2.845150499.1557673672; _ga=GA1.2.421634; _gat=1; CloudFront-Expires=1557843191; CloudFront-Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZG4uaW1hZ2UuODEyMi5qcC92MS8qLzgxMjJqcC8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTU3ODQzMTkxfX19XX0_; CloudFront-Signature=Rl0Wu82VvP1QEpL7hd%7ELhlanwmBlNTPIYodG6wn1NhJH3Ea-V2EaqMkM%7E93uw9%7EU-IkV6Qn3pUvrxgKJdYWHuEDKBu622%7ENwvUWd0jZg-t0VY23-8BAQLO6uLTLBh8L2aOAxe1bXgBQt3bfpgRKYEbY8sySQGK%7Eg5L2BChG%7E1bCNHuAYTqgqf-UBEZX4SBrDJXvwVsazmEvGk-%7Ez6a4y6iWuJ2Pvxh7A9LvGRKgOPR6rQ3bq6Zf4XI6nd8ml-5umo0gy6WKO9%7E7RcPfA68%7ED9sK02OSWZ1xXP51S6xEYIC9bUI1WRRcgu64szJiwtkmh3gjOq9-i27tEu7N10E0VWg__"

GROUP_ID = 1762


def add_default_header(req):
    req.add_header('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
    req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
    req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)


def image_file_change(root_image_file_path, new_root_image_file_path):

    im = Image.open(root_image_file_path)
    im_rgb = im.convert('RGB')
    im_l = ImageOps.invert(im_rgb)

    im_s = ImageEnhance.Sharpness(im_l)
    im_s_e = im_s.enhance(0.01)

    im_br = ImageEnhance.Brightness(im_s_e)
    im_br_e = im_br.enhance(4.0)

    im_con = ImageEnhance.Contrast(im_br_e)
    im_con_e = im_con.enhance(5.0)

    im_con_e.save(new_root_image_file_path, quality=95)


def exe_ocr(image_file_path):
    tools = pyocr.get_available_tools()
    tool = tools[0]
    img_org = Image.open(image_file_path)
    builder = pyocr.builders.TextBuilder()
    result = tool.image_to_string(img_org, lang="eng", builder=builder)

    return result


def get_image_str(root_image_file_path):

    new_root_image_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "new_root_html.jpg")

    image_file_change(root_image_file_path, new_root_image_file_path)

    result = exe_ocr(new_root_image_file_path)

    return result


def get_root_html(opener):

    req = urllib.request.Request(settings.URL_ROOT)
    add_default_header(req)
    res = opener.open(req)

    root_html_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "root_html.html")
    with open(root_html_file_path, mode="wb") as f:
        f.write(res.read())

    with open(root_html_file_path, mode="r", encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    login_image_url = soup.find("img", {"class": "top-security-code-img"})["src"]
    req = urllib.request.Request(login_image_url)
    add_default_header(req)
    res = opener.open(req)

    root_image_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "root_html.jpg")

    with open(root_image_file_path, mode="wb") as f:
        f.write(res.read())

    phrase = get_image_str(root_image_file_path)

    return phrase


def login_main(opener, login_id, password, phrase):

    url_login = '{}{}'.format(settings.URL_ROOT, "front/common/login.html")

    post = {
        'process': '',
        'token': '',
        'sampleId': '',
        'login_id': login_id,
        'password': password,
        'phrase': phrase,
    }

    req = urllib.request.Request(url_login)
    add_default_header(req)
    req.add_header('Referer', settings.URL_ROOT)

    print("url_login", url_login)
    data = urllib.parse.urlencode(post).encode('utf-8')
    with opener.open(req, data) as res:
        result = res.read()


# @utility.try_again(3, 5.0)
def get_photo_param(opener, photo_no):

    GROUP_ID = 1762

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "photo_{}.json".format(photo_no))

    if not os.path.isfile(file_path):

        get_photo_url = "{}{}".format(settings.URL_ROOT, r"api/photo/get/photo.html")

        post = {
            'photoListGetType': "FRONT_GROUP_DETAIL_GROUP_ID",
            'pageId': 1,
            "photoId": "{:0=4}::{:0=4}.jpg".format(GROUP_ID, photo_no),
        }

        req = urllib.request.Request(get_photo_url)
        add_default_header(req)
        req.add_header('Referer', "{}{}".format(settings.URL_ROOT, r"front/group/change.html?nextAction=front_group_detail&group_id=1762&thumbnail_type=230"))
        data = urllib.parse.urlencode(post).encode('utf-8')

        with opener.open(req, data) as res:
            with open(file_path, mode="wb") as f:
                f.write(res.read())

        """
        with open(file_path, mode="wb") as f:
            f.write(result)
        """

    json_data = None
    if os.path.isfile(file_path):
        with open(file_path, mode="r") as f:
            try:
                json_data = json.loads(f.read())
            except:
                print("json read error ({})".format(file_path))

    photo_key_enc = json_data["content"]["photo"]["options"]["zoomUrl"]["image02"]["urlQueryList"]["photoKeyEnc"]
    onetime_key = json_data["content"]["onetimeKey"]

    print(photo_key_enc, onetime_key)

    return photo_key_enc, onetime_key

# @utility.try_again(3, 5.0)


def get_generator(opener, photo_no, photo_key_enc, onetime_key):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "photo_gen_{}.gzip".format(photo_no))
    file_base64_json_path = os.path.join(settings.PICTURE_TEMP_PATH, "photo_base64_{}.json".format(photo_no))

    if not os.path.isfile(file_path):

        get_photo_url = "{}{}".format(settings.URL_ROOT, r"api/photo/generator.html")

        post = {
            'framePatternId': 0,
            'onetimeKey': onetime_key,
            "photoKeyEnc": photo_key_enc,
            "photoframeIndex": "",
            "printsizeLong": 0,
            "printsizeShort": 0,
        }

        req = urllib.request.Request(get_photo_url)
        req.add_header('Referer', "{}{}".format(settings.URL_ROOT, r"front/group/change.html?nextAction=front_group_detail&group_id=1762&thumbnail_type=230"))
        add_default_header(req)
        # req.add_header("Accept-Encoding", "gzip, deflate, br")
        # req.add_header("Content-Type", "application/json;charset=UTF-8")
        # req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
        # req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

        data = bytes(json.dumps(post), "utf-8")

        from gzip import GzipFile

        with opener.open(req, data) as res:
            with open(file_path, mode="wb") as f:
                new_data = res.read()
                f.write(new_data)

            with open(file_path, mode="rb") as fr:
                with open(file_base64_json_path, mode="wb") as fw:
                    with GzipFile(fileobj=fr, mode='rb') as gf:
                        fw.write(gf.read())

                #new_data = res.read()
                # f.write(new_data)

    with open(file_base64_json_path, mode="r") as f:
        json_object = json.load(f)

    import base64

    for i, base64_data in enumerate(json_object["data"]):
        file_base64_json_path = os.path.join(settings.PICTURE_TEMP_PATH, "photo_base64_{}_{}.jpg".format(photo_no, i))
        with open(file_base64_json_path, "wb") as f:
            main_base64_data = base64_data[23:]
            f.write(base64.b64decode(main_base64_data))

    """
    json_data = None
    if os.path.isfile(file_path):
        with open(file_path, mode="r") as f:
            try:
                json_data = json.loads(f.read())
            except:
                print("json read error ({})".format(file_path))
    """

    # pprint.pprint(json_data)

    return


# @utility.try_again(3, 5.0)
def get_category_list(opener, page_no):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "change_{}.html".format(page_no))

    if not os.path.isfile(file_path):

        parse_result = urllib.parse.urlparse("{}{}".format(settings.URL_ROOT, r"front/group/change.html"))

        query_dict = {
            'nextAction': 'front_group_detail'
        }

        scheme, netloc, path, params, _, fragment = parse_result
        query = urllib.parse.urlencode(query_dict)

        url = urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))

        req = urllib.request.Request(url)
        referer_url = "{}{}".format(settings.URL_ROOT, r"front/page/index.html?loginType=1&page_type=home&page_path=index")
        add_default_header(req)
        req.add_header('Referer', referer_url)

        res = opener.open(req)

        with open(file_path, mode="wb") as f:
            f.write(res.read())

    with open(file_path, mode="r", encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    photo_element_list = soup.find_all("div", {"class": "photo"})
    for photo_element in photo_element_list:
        img_element = photo_element.find("a").find("img")
        print(img_element["onload"])

    """
    category_no_tag_list = soup.find_all("li", {"class": "p-categoryList_category"})
    event_info = soup.find("span", {"class": "p-eventInfo_content"})


    date_kanji = event_info.text

    year_month_date = get_date(date_kanji)

    category_no_list = [category_no_tag["data-categoryno"] for category_no_tag in category_no_tag_list]


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

    # return category_no_list, year_month_date


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


def login(login_id, password, local_test_flag):

    if local_test_flag:
        return None

    cookie_jar = http.cookiejar.MozillaCookieJar(COOKIE_FILE_PATH)
    cookie_jar.load()

    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(cookie_processor)

    phrase = get_root_html(opener)

    login_main(opener, login_id, password, phrase)

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

    login_id = "bora010"
    password = "bbb010"
    opener = login(login_id, password, local_test_flag)

    photo_no = 4
    photo_key_enc, onetime_key = get_photo_param(opener, photo_no)
    get_generator(opener, photo_no, photo_key_enc, onetime_key)

    # get_category_list()
    print("end")
    return

    """
    for eventno in eventno_list:
        categoryno_list, year_month_date = get_category_list(opener, eventno)

        for categoryno in categoryno_list:
            print(eventno, categoryno)
            json_data_list = get_picture_list(opener, eventno, categoryno)
            # pprint.pprint(json_data_list)
            for i, json_data in enumerate(json_data_list):
                download_pics(opener, eventno, categoryno, i * 100, json_data, year_month_date)

    print("end")
    """


def read():

    file_path = "C:/Users/nkinta/Desktop/hi_cheese_temp/test.json"
    with open(file_path, mode="r") as f:
        json_data = json.loads(f.read())
        pprint.pprint(json_data)


if __name__ == "__main__":
    main()
