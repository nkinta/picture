
from __future__ import print_function

import os

"""
MOVIE_INPUT_PATH_LIST = [r"D:\movie_workspace\move_web_sample",
                         r"\\NK-PC\picture2\movie_strage\a7s2movie_xavc_50"
                         ]
IMAGE_INPUT_PATH_LIST = [r"D:\movie_workspace\image_web_sample\strage", ]

"""

MOVIE_INPUT_PATH_LIST = [(r"D:\movie_workspace\image_web_sample\movie_strage", r".+(?:(?:goprohero6_[0-9]{2})|(?:goprohero6_[0-9]{2}))\\.+\.\w+$"),
                         ]

IMAGE_INPUT_PATH_LIST = []

OUTPUT_PATH = r"D:\web_servert_test"

WEB_ROOT_PATH = os.path.join(OUTPUT_PATH, "web_root")

FAV_ROOT_PATH = os.path.join(OUTPUT_PATH, "fav_root")

FFMPEG_PATH = r"D:\movie_workspace\ffmpeg\bin\ffmpeg.exe"
