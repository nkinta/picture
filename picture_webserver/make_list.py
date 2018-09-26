
from __future__ import print_function

import os
import datetime
import pprint
import utility
import json
import itertools

from picture_webserver import image_converter as ic
from picture_webserver import movie_converter as mc

from picture_webserver.config import *

# import define
# jpeg_tag_dict = {v[2] : v for v in define.tag_list}

DEFAULT = "DEFAULT"
FFMPEG = "FFMPEG"

THUMBNAIL_DEPOT = os.path.join(cf.OUTPUT_PATH, "thumbnail_depot")

INFO_FILE_NAME = "info.json"

LOCAL_DEPOT_PATH = os.path.join(cf.OUTPUT_PATH, "depot")
STOP_FILE_PATH = os.path.join(LOCAL_DEPOT_PATH, "stop.txt")
START_FILE_PATH = os.path.join(LOCAL_DEPOT_PATH, "start.txt")

IS_CREATE_REF = True


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, "to_json"):
            return o.to_json()

        return json.JSONEncoder.default(self, o)


class FavJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, "to_fav_json"):
            return o.to_fav_json()

        return json.JSONEncoder.default(self, o)


class AccessJsonEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, "to_access_json"):
            return o.to_access_json()

        return json.JSONEncoder.default(self, o)


#vJSON_ENCODER = json.JSONEncoder(default=json_enc_default)


class Error(Exception):
    pass


class FolderInfo():

    def __init__(self, name):
        self.name = name

    def get_path(self):
        return os.path.join(".", self.name)

    def get_name(self):
        return self.name

    def __to_json_common(self):
        result = {
            "name": self.name,
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children_info_path": "{}/".format(self.get_path().replace("\\", "/")),
        }
        return result

    def to_json(self):
        return self.__to_json_common()

    def to_fav_json(self):
        return self.__to_json_common()

    def to_access_json(self):
        return self.__to_json_common()


class ImageFileInfo():

    @classmethod
    def get_directory_name(cls):
        return "images"

    def __init__(self, dt, local_path):
        self.dt = dt
        self.local_path = local_path

    def get_name(self):
        name = os.path.basename(os.path.splitext(self.local_path)[0])
        return name

    def get_id(self):
        basename = self.get_name()
        dirname = os.path.basename(os.path.dirname(self.local_path))
        id = "{}_{}".format(dirname, basename)
        return id

    def get_path(self):
        return os.path.join(".", self.get_name())

    def get_size(self):
        return os.path.getsize(self.local_path)

    def get_info_local_path(self):
        temp_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "info", *(self.get_id().split("_")))
        result_path = "{}{}".format(temp_path, ".info")
        return result_path

    def get_medium_local_path(self):
        temp_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "jpg_medium", *(self.get_id().split("_")))
        result_path = "{}{}".format(temp_path, ".jpg")
        return result_path

    def get_thumbnail_local_path(self):
        temp_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "thumbnail", *(self.get_id().split("_")))
        result_path = "{}{}".format(temp_path, ".jpg")
        return result_path

    def get_jpg_local_path(self):
        temp_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "jpg", *(self.get_id().split("_")))
        result_path = "{}{}".format(temp_path, ".jpg")
        return result_path

    def to_json(self):
        result = {
            # "id": self.get_id(),
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "time": self.dt.strftime('%Y%m%d%H%M'),
            "children": [
                {"name": "arw",
                 "path": "arw/",
                 "download_filename": "picture.arw",
                 "mimetype": "application/octet-stream",
                 "attachment": True,
                 "attachment_filename": "{}.arw".format(self.get_id()),
                 "local_path": self.local_path,
                 "size": self.get_size()
                 },
                {"name": "jpg",
                 "path": "jpg/",
                 "download_filename": "picture.jpg",
                 "mimetype": "image/jpeg",
                 "attachment_filename": "{}.jpg".format(self.get_id()),
                 "local_path": self.get_jpg_local_path(),
                 },
                {"name": "jpg_medium",
                 "path": "jpg_medium/",
                 "download_filename": "picture_medium.jpg",
                 "mimetype": "image/jpeg",
                 "local_path": self.get_medium_local_path(),
                 },
                {"name": "thumbnail",
                 "path": "thumbnail/",
                 "download_filename": "thumbnail.jpg",
                 "mimetype": "image/jpeg",
                 "local_path": self.get_thumbnail_local_path(),
                 },
                {"name": "exif_info",
                 "path": "exif_info/",
                 "download_filename": "exif_info.json",
                 "mimetype": "application/json",
                 "local_path": self.get_info_local_path(),
                 },
            ]
        }
        return result

    def to_fav_json(self):
        result = {
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children": [],
        }
        return result

    def to_access_json(self):
        result = {
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children": [],
        }
        return result


class MovieFileInfo():

    @classmethod
    def get_directory_name(cls):
        return "movies"

    def __init__(self, dt, local_path):
        self.dt = dt
        self.local_path = local_path

    def get_id(self):
        basename = self.get_name()
        # dirname = os.path.basename(os.path.dirname(self.local_path))
        dirname = _get_one_day_directory_name(self.dt)
        id = "{}_{}".format(dirname, basename)
        return id

    def get_path(self):
        return os.path.join(".", self.get_name())

    def get_name(self):
        name = os.path.basename(os.path.splitext(self.local_path)[0])
        return name

    def get_thumbnail_local_path(self, type=DEFAULT):
        directory_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "thumbnail", *(self.get_id().split("_")))
        if type == DEFAULT:
            return os.path.join(directory_path, "img_001.jpg")
        elif type == FFMPEG:
            return os.path.join(directory_path, "img_%03d.jpg")

    def get_movie_small_local_path(self, type=DEFAULT):
        temp_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "movie_small", *(self.get_id().split("_")))
        result_path = "{}{}".format(temp_path, ".mp4")
        return result_path

    def get_movie_medium_local_path(self, type=DEFAULT):
        temp_path = os.path.join(LOCAL_DEPOT_PATH, self.get_directory_name(), "movie_medium", *(self.get_id().split("_")))
        result_path = "{}{}".format(temp_path, ".mp4")
        return result_path

    def get_size(self):
        return os.path.getsize(self.local_path)

    def to_json(self):
        result = {
            # "id": self.get_id(),
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "time": self.dt.strftime('%Y%m%d%H%M'),
            "children": [
                {"name": "thumbnail",
                 "path": "thumbnail/",
                 "download_filename": "thumbnail_main.jpg",
                 "mimetype": "image/png",
                 "local_path": self.get_thumbnail_local_path(),
                 },
                {"name": "movie_small",
                 "path": "movie_small/",
                 "download_filename": "movie_small.mp4",
                 "mimetype": "video/mp4",
                 "attachment_filename": "{}_small.mp4".format(self.get_id()),
                 "local_path": self.get_movie_small_local_path(),
                 },
                {"name": "movie_medium",
                 "path": "movie_medium/",
                 "download_filename": "movie_medium.mp4",
                 "mimetype": None,
                 "attachment": True,
                 "attachment_filename": "{}_medium.mp4".format(self.get_id()),
                 "local_path": self.get_movie_medium_local_path(),
                 },
                {"name": "movie",
                 "path": "movie/",
                 "download_filename": "movie.mp4",
                 "mimetype": None,
                 "attachment": True,
                 "attachment_filename": "{}.mp4".format(self.get_id()),
                 "local_path": self.local_path,
                 "size": self.get_size()
                 },
            ]
        }
        return result

    def to_fav_json(self):
        result = {
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children": [],
        }
        return result

    def to_access_json(self):
        result = {
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children": [],
        }
        return result

    def __repr__(self):
        return str(self.__dict__)


def is_stop_process():
    if os.path.isfile(STOP_FILE_PATH):
        return True
    else:
        return False


def stop_process():
    if os.path.isfile(START_FILE_PATH):
        os.rename(START_FILE_PATH, STOP_FILE_PATH)


def start_process():
    if os.path.isfile(STOP_FILE_PATH):
        os.rename(STOP_FILE_PATH, START_FILE_PATH)


def toggle_process():
    if is_stop_process():
        print("start")
        start_process()
    else:
        print("stop")
        stop_process()


def _get_one_day_directory_name(dt):
    one_day = (dt.year, dt.month, dt.day)
    directory_name = '{}_{:0>2}{:0>2}'.format(*one_day)
    return directory_name


def _create_image_ref_data_execute(file_info_list_by_date):

    func_list = [
        lambda v: ic.create_image_jpg(v.local_path, v.get_jpg_local_path()),
        lambda v: ic.create_image_middle_jpg(v.get_jpg_local_path(), v.get_medium_local_path()),
        lambda v: ic.create_image_small_jpg(v.get_medium_local_path(), v.get_thumbnail_local_path()),
        lambda v: ic.create_image_info(v.get_jpg_local_path(), v.get_info_local_path())
    ]

    for func in func_list:
        if is_stop_process():
            continue
        for one_day, file_info_list in file_info_list_by_date.items():
            if is_stop_process():
                continue
            for file_info in file_info_list:
                if is_stop_process():
                    continue
                func(file_info)
            # return


def _create_movie_ref_data_execute(file_info_list_by_date):

    func_list = [
        lambda v: mc.create_movie_small("1920", "4000k", "128k", v.local_path, v.get_movie_medium_local_path(FFMPEG)),
        lambda v: mc.create_movie_small("960", "400k", "64k", v.get_movie_medium_local_path(FFMPEG), v.get_movie_small_local_path(FFMPEG)),
        lambda v: mc.create_movie_thumbnail(v.get_movie_small_local_path(FFMPEG), v.get_thumbnail_local_path(FFMPEG)),
    ]
    for func in func_list:
        if is_stop_process():
            continue
        for one_day, file_info_list in file_info_list_by_date.items():
            if is_stop_process():
                continue
            for file_info in file_info_list:
                if is_stop_process():
                    continue
                func(file_info)

    """
    for one_day, file_info_list in file_info_list_by_date.items():
        for file_info in file_info_list:
            _create_movie_small("960", "400k", "64k", file_info.get_movie_medium_local_path(FFMPEG), file_info.get_movie_small_local_path(FFMPEG))

    for one_day, file_info_list in file_info_list_by_date.items():
        for file_info in file_info_list:
            # = file_info
            # output_file_path = os.path.join(THUMBNAIL_DEPOT, file_info.get_thumbnail_path(), "img_%03d.png")
            # __create_thumbnail(file_info.local_path, output_file_path)

            _create_movie_thumbnail(file_info.get_movie_small_local_path(FFMPEG), file_info.get_thumbnail_local_path(FFMPEG))
    """


def _create_info_file_all(file_info_list_by_date, cls):

    _create_info_file(cf.WEB_ROOT_PATH, JsonEncoder, file_info_list_by_date, cls)
    _create_info_file(cf.FAV_ROOT_PATH, FavJsonEncoder, file_info_list_by_date, cls)
    _create_info_file(cf.ACCESS_ROOT_PATH, AccessJsonEncoder, file_info_list_by_date, cls)


def _create_info_file(root_path, json_encoder, file_info_list_by_date, cls):

    output_file_path = os.path.join(root_path, INFO_FILE_NAME)

    utility.make_directory(output_file_path)
    date_list = [FolderInfo(v) for v, _ in file_info_list_by_date.items()]
    write_data = json.dumps(date_list, cls=json_encoder, indent="  ", )
    with open(output_file_path, "w") as fp:
        fp.write(write_data)

    for one_day, file_info_list in file_info_list_by_date.items():

        output_file_path = os.path.join(root_path, one_day, cls.get_directory_name(), INFO_FILE_NAME)
        utility.make_directory(output_file_path)
        write_data = json.dumps(file_info_list, cls=json_encoder, indent="  ",)
        with open(output_file_path, "w") as fp:
            fp.write(write_data)

    for root, dirs, files in os.walk(root_path):
        if not dirs:
            continue
        folder_list = [FolderInfo(os.path.basename(v)) for v in dirs]
        write_data = json.dumps(folder_list, cls=json_encoder, indent="  ",)
        with open(os.path.join(root, INFO_FILE_NAME), "w") as fp:
            fp.write(write_data)


def _create_file_info_list(input_path_list, ext_list, cls):

    file_path_list_list = []
    for input_path_info in input_path_list:
        input_path, filtering = input_path_info
        file_path_list_list.append(utility.directory_walk(input_path, ext_list, filtering, 2))

    file_path_list = itertools.chain.from_iterable(file_path_list_list)

    file_info_list = []

    for file_path in file_path_list:
        dt = datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)
        print(file_path, dt.strftime('%Y%m%d%H%M'))
        file_info_list.append(cls(dt, file_path))

    sorted_file_info_list = sorted(file_info_list, key=lambda v: v.dt)

    file_info_list_by_date = {}
    for file_info in sorted_file_info_list:
        dt = file_info.dt
        file_path = file_info.local_path
        one_day = _get_one_day_directory_name(dt)
        file_list = file_info_list_by_date.get(one_day, None)
        if file_list is None:
            file_list = []
            file_info_list_by_date[one_day] = file_list

        file_list.append(file_info)

    return file_info_list_by_date


def main():

    # file_info_list_by_date = _create_file_info_list(cf.MOVIE_INPUT_PATH, (".MP4", ".mp4"), MovieFileInfo) # (".MP4", ".mp4")
    temp_image = _create_file_info_list(cf.IMAGE_INPUT_PATH_LIST, (".ARW", ".arw"), ImageFileInfo)
    _create_info_file_all(temp_image, ImageFileInfo)

    temp_movie = _create_file_info_list(cf.MOVIE_INPUT_PATH_LIST, (".MP4", ".mp4"), MovieFileInfo)  # (".MP4", ".mp4")
    _create_info_file_all(temp_movie, MovieFileInfo)

    # pprint.pprint(file_info_list_by_date)
    if IS_CREATE_REF:
        _create_image_ref_data_execute(temp_image)
        _create_movie_ref_data_execute(temp_movie)

    print("end")
    # __create_ref_data_execute(temp_movie)
    # print(file_list)


if __name__ == "__main__":
    main()
