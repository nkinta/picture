
from __future__ import print_function

import os
import struct
import re

import utility
import define
import shutil

YEAR = "2018_"


class Error(Exception):
    pass


def all_execute(input_directory_path, output_directory_path):

    prog = re.compile(r"\d{4}(\d{4})$")

    pass_already_exist_flag = True
    new_ext = ".jpg"

    input_file_path_list = utility.directory_walk(input_directory_path, [".ARW", ".arw", ".JPG", ".jpg"])
    print(input_file_path_list)

    for input_file_path in input_file_path_list:
        temp_output_file_path_1 = os.path.join(output_directory_path, os.path.relpath(input_file_path, input_directory_path))
        temp_output_file_path_2 = os.path.normpath(temp_output_file_path_1)
        temp_output_directory_path = os.path.dirname(temp_output_file_path_2)
        temp_output_file_name = os.path.basename(temp_output_file_path_2)

        temp_file_path_tuple = temp_output_directory_path.split(os.path.sep)
        temp_output_directory_name = temp_file_path_tuple[-1]
        m = prog.match(temp_output_directory_name)
        if m:
            temp_new_output_directory_name = "%s%s" % (YEAR, m.group(1))
        else:
            if (True):
                print("wring directory name (%s)" % temp_output_directory_name)
                continue
            else:
                raise Error("wring directory name (%s)" % temp_output_directory_name)

        output_file_path = os.path.sep.join((temp_file_path_tuple[:-1] + [temp_new_output_directory_name, temp_output_file_name]))

        print("copy (%s) -> (%s)" % (input_file_path, output_file_path))
        if pass_already_exist_flag:
            if os.path.isfile(output_file_path) == True:
                if os.path.getsize(input_file_path) == os.path.getsize(output_file_path):
                    print("pass %s" % output_file_path)
                    continue
                else:
                    print(output_file_path)
                    output_file_path = "%s_%s%s" % (os.path.splitext(output_file_path)[0], 2, os.path.splitext(output_file_path)[1])

        directory = os.path.dirname(output_file_path)
        if os.path.isdir(directory) == False:
            os.makedirs(directory)

        shutil.move(input_file_path, output_file_path)
        """
        if os.path.isfile(output_file_path) == True:
            print("delete %s" % input_file_path)
            os.remove(input_file_path)
        """
        # arw_convert(input_file_path, output_file_path)
    print("end")


def main():

    input_directory_path = r"U:\dcim"
    output_directory_path = os.path.join(r"M:\picture", "strage")
    all_execute(input_directory_path, output_directory_path)


if __name__ == "__main__":
    main()
