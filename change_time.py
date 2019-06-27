
from __future__ import print_function

import os
import struct

import utility
import define

import datetime


class Error(Exception):
    pass


def offset_time(file_path, offset_date, offset_our):

    path_stat = os.stat(file_path)
    our_offset = 60 * 60
    date_offset = 24 * 60 * 60
    offset = offset_our * our_offset + offset_date * date_offset

    os.utime(file_path, (path_stat.st_atime + offset, path_stat.st_mtime + offset))


def all_execute(offset_date, offset_our, input_directory_path, exr_list):

    input_file_path_list = utility.directory_walk(input_directory_path, exr_list)

    for input_file_path in input_file_path_list:
        offset_time(input_file_path, offset_date, offset_our)


def main():

    offset_date = 30
    offset_our = 8
    input_directory_path = r""
    all_execute(offset_date, offset_our, input_directory_path, [".MP4", ".mp4"])


"""
def main():

    file_path = r"C:\Users\nkinta\Desktop\imagedata_change\ldv_p\arw\DSC01196.ARW"

    path_stat = os.stat(file_path)

    print(path_stat)
    print(dir(path_stat))
    print(path_stat.st_atime, datetime.datetime.fromtimestamp(path_stat.st_atime))
    print(path_stat.st_mtime, datetime.datetime.fromtimestamp(path_stat.st_mtime))
    print(path_stat.st_ctime, datetime.datetime.fromtimestamp(path_stat.st_ctime), datetime.datetime.fromtimestamp(path_stat.st_ctime + 24 * 3600))

    date_offset = 24 * 60 * 60
    plus_date = 30

    os.utime(file_path, (path_stat.st_atime + (plus_date * date_offset), path_stat.st_mtime + (plus_date * date_offset)))
"""


if __name__ == "__main__":
    main()
