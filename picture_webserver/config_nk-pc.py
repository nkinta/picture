
from __future__ import print_function

import os

"""
MOVIE_INPUT_PATH_LIST = [r"D:\movie_workspace\move_web_sample",
                         r"\\NK-PC\picture2\movie_strage\a7s2movie_xavc_50"
                         ]
IMAGE_INPUT_PATH_LIST = [r"D:\movie_workspace\image_web_sample\strage", ]

"""

directory_name_list = ["goprohero6_[0-9]{2}",
                       "a7s2movie_xavc_[0-9]{2}",
                       "a7s2movie_mp4_[0-9]{2}",
                       "a5100movie_xavc_[0-9]{2}",
                       "a5100movie_mp4_[0-9]{2}",
                       "fdrx1000v_[0-9]{2}",
                       "fdrx1000v_xavc_[0-9]{2}",
                       "handycam_hfm51_[0-9]{2}",
                       "osmo_[0-9]{2}",
                       "as200v_[0-9]{2}",
                       ]

directory_name_match = "|".join(["(?:{})".format(v) for v in directory_name_list])

"""
MOVIE_INPUT_PATH_LIST = [(r"M:\picture\movie_strage", r".+(?:{})\\.+\.\w+$".format(directory_name_match)),
                         ]
"""
MOVIE_INPUT_PATH_LIST = [(r"M:\picture\movie_strage", r".+(?:{})\\.+\.\w+$".format("goprohero6_08")),
                         ]

IMAGE_INPUT_PATH_LIST = [(r"M:\picture\strage", r".+(?:201[0-9]_[0-9]{4})\\.+\.\w+$")]

OUTPUT_PATH = r"W:\web_servert_test"

WEB_ROOT_PATH = os.path.join(OUTPUT_PATH, "web_root")

FAV_ROOT_PATH = os.path.join(OUTPUT_PATH, "fav_root")

FFMPEG_PATH = r"W:\movie_workspace\ffmpeg\bin\ffmpeg.exe"
