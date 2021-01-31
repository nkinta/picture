
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

PAGE_NUM = 20


class Error(Exception):
    pass


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


@utility.try_again(3, 5.0)
def get_root_main(opener, file_path):
    req = urllib.request.Request(settings.URL_ROOT)
    add_default_header(req)
    with opener.open(req) as res:
        data = res.read()

    with open(file_path, mode="wb") as f:
        f.write(data)


def get_root_html(opener):

    root_html_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "root_html.html")
    get_root_main(opener, root_html_file_path)

    with open(root_html_file_path, mode="r", encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    login_image_url = soup.find("img", {"class": "top-security-code-img"})["src"]
    req = urllib.request.Request(login_image_url)
    add_default_header(req)

    with opener.open(req) as res:
        root_image_file_path = os.path.join(settings.PICTURE_TEMP_PATH, "root_html.jpg")

        with open(root_image_file_path, mode="wb") as f:
            f.write(res.read())

    phrase = get_image_str(root_image_file_path)
    print("phrase -> ", phrase)

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
    print("phrase -> ", phrase)
    with opener.open(req, data) as res:
        result = res.read()
        print(result)


@utility.try_again(3, 5.0)
def get_photo_param(opener, group_id, photo_no, photo_page_offset, jpg_upper_case):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "g_{}".format(group_id), "photo_param", "photo_{}.json".format(photo_no))

    if True:  # not os.path.isfile(file_path):

        get_photo_url = "{}{}".format(settings.URL_ROOT, r"api/photo/get/photo.html")

        page_id = (photo_no - photo_page_offset - 1) // PAGE_NUM + 1

        jpg_string = "jpg"
        if jpg_upper_case:
            jpg_string = jpg_string.upper()

        post = {
            'photoListGetType': "FRONT_GROUP_DETAIL_GROUP_ID",
            'pageId': page_id,
            "photoId": "{:0=4}::{:0=4}.{}".format(group_id, photo_no, jpg_string),
        }

        print("", post)

        req = urllib.request.Request(get_photo_url)
        add_default_header(req)
        # req.add_header('Referer', "{}{}".format(settings.URL_ROOT, r"front/group/change.html?nextAction=front_group_detail&group_id={}&thumbnail_type=230").format(group_id))
        # https://phst.jp/yazawa/front/group/change.html?group_id=2176&nextAction=front_group_detail&pageID=1
        req.add_header('Referer', "{}{}".format(settings.URL_ROOT, r"front/group/change.html?nextAction=front_group_detail&group_id={}&pageID={}").format(group_id, page_id))
        data = urllib.parse.urlencode(post).encode('utf-8')

        with opener.open(req, data) as res:
            utility.make_directory(file_path)
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

    pprint.pprint(json_data)
    photo_key_enc = json_data["content"]["photo"]["options"]["zoomUrl"]["image02"]["urlQueryList"]["photoKeyEnc"]
    onetime_key = json_data["content"]["onetimeKey"]

    print(photo_key_enc, onetime_key)

    return photo_key_enc, onetime_key


def get_base64_json_path(group_id, photo_no):
    json_path = os.path.join(settings.PICTURE_TEMP_PATH, "g_{}".format(group_id), "pic_json", "photo_base64_{}.json".format(photo_no))

    return json_path


def get_split_jpg_path(group_id, photo_no, split_index):
    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "g_{}".format(group_id), "pic_temp", "photo_base64_{}_{}.jpg".format(photo_no, split_index))

    return file_path


def get_generator(opener, group_id, photo_no, photo_key_enc, onetime_key):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "g_{}".format(group_id), "pic_json", "photo_gen_{}.gzip".format(photo_no))
    file_base64_json_path = get_base64_json_path(group_id, photo_no)

    if True:  # not os.path.isfile(file_path):

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
        req.add_header('Referer', "{}{}".format(settings.URL_ROOT, r"front/group/change.html?nextAction=front_group_detail&group_id={}&thumbnail_type=230").format(group_id))
        add_default_header(req)
        # req.add_header("Accept-Encoding", "gzip, deflate, br")
        # req.add_header("Content-Type", "application/json;charset=UTF-8")
        # req.add_header('accept-language', settings.HTTP_HEADER_LANGUAGE)
        # req.add_header('User-Agent', settings.HTTP_HEADER_USER_AGENT)

        data = bytes(json.dumps(post), "utf-8")

        from gzip import GzipFile

        with opener.open(req, data) as res:
            utility.make_directory(file_path)
            with open(file_path, mode="wb") as f:
                new_data = res.read()
                f.write(new_data)

            with open(file_path, mode="rb") as fr:
                utility.make_directory(file_base64_json_path)
                with open(file_base64_json_path, mode="wb") as fw:
                    with GzipFile(fileobj=fr, mode='rb') as gf:
                        fw.write(gf.read())

                #new_data = res.read()
                # f.write(new_data)

    with open(file_base64_json_path, mode="r") as f:
        json_object = json.load(f)

    import base64

    jpg_path_list = []
    for i, base64_data in enumerate(json_object["data"]):
        file_base64_jpg_path = get_split_jpg_path(group_id, photo_no, i)
        jpg_path_list.append(file_base64_jpg_path)
        utility.make_directory(file_base64_jpg_path)
        with open(file_base64_jpg_path, "wb") as f:
            main_base64_data = base64_data[23:]
            f.write(base64.b64decode(main_base64_data))

    return jpg_path_list, json_object


def get_category_list(opener, group_id):

    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "change_{}.html".format(group_id))

    if True:

        parse_result = urllib.parse.urlparse("{}{}".format(settings.URL_ROOT, r"front/group/change.html"))

        query_dict = {
            'nextAction': 'front_group_detail',
            "group_id": group_id,
            "gm_visible": "gm_b_1::1,gm_b_2::1,gm_b_3::1"
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

    # return category_no_list, year_month_date

COMBINE_V, COMBINE_H = range(2)


def combine_file(file_path_list, target_file_path, mergin, v_or_h):

    if v_or_h == COMBINE_V:
        height_name = "height"
        width_name = "width"
    elif v_or_h == COMBINE_H:
        height_name = "width"
        width_name = "height"

    def calc_total_height(height_name, width_name):
        total_height = 0
        width = getattr(im_list[0], width_name)
        for im in im_list:
            total_height = total_height + getattr(im, height_name)
            if width != getattr(im, width_name):
                raise Error("width difference {} != {}".format(width, getattr(im, width_name)))
        return total_height, width

    im_list = []
    for file_path in file_path_list:
        im_list.append(Image.open(file_path))

    mergin_total = mergin * (len(file_path_list) - 1)

    total_height, width = calc_total_height(height_name, width_name)

    if v_or_h == COMBINE_V:
        target_image = Image.new("RGB", (width, total_height - mergin_total))
    elif v_or_h == COMBINE_H:
        target_image = Image.new("RGB", (total_height - mergin_total, width))

    current_height = 0
    for im in im_list:
        if v_or_h == COMBINE_V:
            target_image.paste(im, (0, current_height))
        elif v_or_h == COMBINE_H:
            target_image.paste(im, (current_height, 0))

        current_height = current_height + getattr(im, height_name) - mergin

    utility.make_directory(target_file_path)
    target_image.save(target_file_path)
    # out_image.show()


def login(login_id, password, local_test_flag, do_login_flag):

    if local_test_flag:
        return None

    cookie_jar = http.cookiejar.MozillaCookieJar(COOKIE_FILE_PATH)
    cookie_jar.load()

    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(cookie_processor)

    if do_login_flag:
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


def get_result_file_path(group_id, photo_no):
    file_path = os.path.join(settings.PICTURE_TEMP_PATH, "g_{}".format(group_id), "picture", "photo_{}.jpg".format(photo_no))

    return file_path


def get_split_dir(json_object):

    combine_direction = COMBINE_V
    if json_object["splits"][0] == 1:
        combine_direction = COMBINE_V
    elif json_object["splits"][1] == 1:
        combine_direction = COMBINE_H

    return combine_direction


def download_pic(opener, group_id, start_no, end_no, photo_page_offset, jpg_upper_case):

    for photo_no in range(start_no, end_no):
        file_path = get_result_file_path(group_id, photo_no)
        photo_key_enc, onetime_key = get_photo_param(opener, group_id, photo_no, photo_page_offset, jpg_upper_case)
        div_file_path_list, json_object = get_generator(opener, group_id, photo_no, photo_key_enc, onetime_key)

        combine_direction = get_split_dir(json_object)

        combine_file(div_file_path_list, file_path, 5, combine_direction)


def combine_only(group_id, start_no, end_no):

    target_override_date = (2020, 10, 5)

    for photo_no in range(start_no, end_no):
        json_path = get_base64_json_path(group_id, photo_no)
        with open(json_path, mode="r") as f:
            json_object = json.load(f)
        num = len(json_object["data"])

        div_file_path_list = []
        for split_index in range(num):
            div_file_path_list.append(get_split_jpg_path(group_id, photo_no, split_index))
        file_path = get_result_file_path(group_id, photo_no)

        combine_direction = get_split_dir(json_object)

        combine_file(div_file_path_list, file_path, 5, combine_direction)

        override_date(file_path, target_override_date)


def main():

    group_id = 2175     # photo.html 2174
    start_pic = 2001
    last_pic = 2012
    jpg_upper_case = False

    """
    group_id = 2174     # photo.html 2174
    start_pic = 1
    last_pic = 10
    start_pic_offset = start_pic - 1

    """

    local_test_flag = False
    do_login_flag = True

    login_id = "bora011"
    password = "bbb011"

    opener = login(login_id, password, local_test_flag, do_login_flag)

    start_pic_offset = start_pic - 1
    get_category_list(opener, group_id)
    download_pic(opener, group_id, start_pic, last_pic, start_pic_offset, jpg_upper_case)

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
