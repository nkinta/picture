# -*- coding: utf-8 -*-

import os
import stat
import subprocess
import time
import shutil
import re

# from ordereddict import OrderedDict


class Error(Exception):
    pass


def create_pack_list(input_directory_path, output_directory_path, file_list, pack_file_ext):
    temp_pack_dict = {}

    for file_path in file_list:
        directory_path = os.path.dirname(file_path)
        temp_pack_file_path = "%s.%s" % (directory_path, pack_file_ext)
        pack_file_path = os.path.join(output_directory_path, os.path.relpath(temp_pack_file_path, input_directory_path))
        if not pack_file_path in temp_pack_dict:
            temp_pack_dict[pack_file_path] = []
        temp_pack_dict[pack_file_path].append(file_path)

    pack_list = []
    for pack_file_path, input_file_path_list in temp_pack_dict.items():
        temp_dict = dict()
        temp_dict["output_pack_file"] = pack_file_path
        temp_dict["input_file_list"] = input_file_path_list
        pack_list.append(temp_dict)

    return pack_list


def directory_walk(input_dirpath, exts, filtering=None, hierarchy=None):

    program = None
    if not filtering is None:
        program = re.compile(filtering)

    print(input_dirpath)

    filepathlist = []
    for root, dirs, files in os.walk(input_dirpath):

        relpath = os.path.relpath(root, input_dirpath)
        if relpath == ".":
            temp_hierarchy = 0
        else:
            relative_directory_list = relpath.split(os.path.sep)
            temp_hierarchy = len(relative_directory_list)

        if hierarchy is not None:
            if hierarchy <= temp_hierarchy:
                del dirs[:]

        print("directory walking :%s, %s" % (root, temp_hierarchy))
        for file in files:
            if program:
                if not program.match(file):
                    continue

            filename, ext = os.path.splitext(file)
            if (exts is None) or (ext in exts):
                fullpath = os.path.join(root, file)
                filepathlist.append(fullpath)
            else:
                continue

    return filepathlist


def get_command_tuple(command):
    temp_string = '""'

    quatation_pattern = "(?P<quotation>[\"'])(.+?)(?P=quotation)"
    quatation_prog = re.compile(quatation_pattern)
    replace_name_list = [item[1] for item in re.findall(quatation_prog, command)]
    replaced_command = re.sub(quatation_pattern, temp_string, command)

    split_pattern = "\S+"
    split_prog = re.compile(split_pattern)
    split_name_list = [item for item in re.findall(split_prog, replaced_command)]

    temp_string_prog = re.compile("([^%s]*)(%s)" % (temp_string, temp_string))

    def replace_name_yield():
        for replace_name in replace_name_list:
            yield replace_name

    temp_gen = replace_name_yield()

    new_split_name_list = []
    for split_name in split_name_list:
        new_split_name = ""
        start, end = 0, 0
        for m in re.finditer(temp_string_prog, split_name):
            start, end = m.span(0)
            new_split_name += split_name[start: end - len(temp_string)] + temp_gen.next()
        else:
            new_split_name += split_name[end:]

        new_split_name_list.append(new_split_name)

    command_tuple = tuple(new_split_name_list)

    return command_tuple


def create_process(command, call_back, interval=0.5, trycount=10, env=None):
    '''!
    @brief プロセス作成する関数
    　　タイムアウト対応
    threadとしてこの関数を渡すようにもできるように、callback引数がある
    @param command　
    @param call_back　実行が終わったらこの関数を呼ぶ
    @param interval 実行が終わったかどうか調査する時間間隔
    @param trycount 実行が終わったかどうか調査する回数
    '''

    def temp_thread_func():

        if isinstance(command, str):
            command_tuple = get_command_tuple(command)
        else:
            command_tuple = tuple([re.sub(r"[\"']", "", result) for result in command])
            # command_tuple = command

        """
        print("command before:", command)
        if isinstance(command, basestring):
            pattern_a = "(?P<quotation>[\"'])(.+?)(?P=quotation)"
            pattern_b = "\S+"
            prog = re.compile(r"((?:%s)|(%s))" % (pattern_a, pattern_b))
            result_list = re.findall(prog, command)
            command_tuple = tuple([re.sub(r"[\"']", "", result[0]) for result in result_list])
        else:
            command_tuple = tuple([re.sub(r"[\"']", "", result) for result in command])
            # command_tuple = command

        print("command end:", command_tuple)
        """

        proc = subprocess.Popen(command_tuple,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                env=env
                                )

        returncode = None
        stdout_message = ""
        for i in range(trycount):
            time.sleep(interval)
            returncode = proc.poll()
            for line in proc.stdout:
                stdout_message += str(line)
            if (returncode != None):
                break

        call_back(returncode, stdout_message)

    return temp_thread_func


def make_directory(file_path):
    directory = os.path.dirname(file_path)
    if os.path.isdir(directory) == False:
        os.makedirs(directory)


def copy_data(source_directory_path, destination_directory_path, source_file_path_list, forceFlag=False):
    '''!
    @brief source_directory_path から、destination_directory_pathへ、階層構造を保ってデータをコピーする
    '''

    destination_file_path_list = []
    for source_file_path in source_file_path_list:
        if source_file_path is None:
            continue

        destination_file_path = os.path.join(destination_directory_path, os.path.relpath(source_file_path, source_directory_path))
        directory, file = os.path.split(destination_file_path)

        if os.path.isdir(directory) == False:
            os.makedirs(directory)
        print("copyed (%s) -> (%s)" % (source_file_path, destination_file_path))
        if forceFlag:
            if os.path.exists(destination_file_path):
                os.chmod(destination_file_path, ~stat.S_IREAD)
        shutil.copyfile(source_file_path, destination_file_path)
        destination_file_path_list.append(destination_file_path)

    return destination_file_path_list
