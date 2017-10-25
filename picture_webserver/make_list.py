
from __future__ import print_function

import os
import http.server
import datetime
import pprint
import utility
import json
import itertools

import config as cf

# import define
# jpeg_tag_dict = {v[2] : v for v in define.tag_list}

DEFAULT = "DEFAULT"
FFMPEG = "FFMPEG"

THUMBNAIL_DEPOT = os.path.join(cf.OUTPUT_PATH, "thumbnail_depot")

WEB_ROOT_PATH = os.path.join(cf.OUTPUT_PATH, "web_root")

INFO_FILE_NAME = "info.json"

LOCAL_DEPOT_PATH = os.path.join(cf.OUTPUT_PATH, "depot")

IS_CREATE_REF = True

class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "to_json"):
            return o.to_json()
       
        return json.JSONEncoder.default(self, o)

#vJSON_ENCODER = json.JSONEncoder(default=json_enc_default)


class Error(Exception):
    pass

class FolderInfo():
        
    def __init__(self, name):
        self.name = name
            
    def get_path(self):
        return os.path.join(".", self.name)

    def to_json(self):
        result = {
            "name": self.name,
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children_info_path": "{}/".format(self.get_path().replace("\\", "/")),
                  }
        return result


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
    
    def __repr__(self):
        return str(self.__dict__)


def _get_one_day_directory_name(dt):
    one_day = (dt.year, dt.month, dt.day)
    directory_name = '{}_{:0>2}{:0>2}'.format(*one_day)
    return directory_name

def _create_image_ref_data_execute(file_info_list_by_date):
    
    func_list = [
        lambda v: _create_image_jpg(v.local_path, v.get_jpg_local_path()),
        lambda v: _create_image_middle_jpg(v.get_jpg_local_path(), v.get_medium_local_path()),
        lambda v: _create_image_small_jpg(v.get_medium_local_path(), v.get_thumbnail_local_path()),
        lambda v: _create_image_info(v.get_jpg_local_path(), v.get_info_local_path())
        ]    
            
    for func in func_list:
        for one_day, file_info_list in file_info_list_by_date.items():
            for file_info in file_info_list:
                func(file_info)
            # return
def _create_movie_ref_data_execute(file_info_list_by_date):

    func_list = [
        lambda v: _create_movie_small("1920", "4000k", "128k", v.local_path, v.get_movie_medium_local_path(FFMPEG)),
        lambda v: _create_movie_small("960", "400k", "64k", v.get_movie_medium_local_path(FFMPEG), v.get_movie_small_local_path(FFMPEG)),
        lambda v: _create_movie_thumbnail(v.get_movie_small_local_path(FFMPEG), v.get_thumbnail_local_path(FFMPEG)),
        ]
    for func in func_list:
        for one_day, file_info_list in file_info_list_by_date.items():
            for file_info in file_info_list:
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


def _create_image_jpg(input_file_path, output_file_path):
    import execute
    execute.arw_convert(input_file_path, output_file_path)


def _create_image_small_jpg(input_file_path, output_file_path):
    from PIL import Image
    
    img = Image.open(input_file_path)
    img.thumbnail((160, 160), Image.ANTIALIAS)
    
    utility.make_directory(output_file_path)
    img.save(output_file_path)


def _create_image_middle_jpg(input_file_path, output_file_path):
    from PIL import Image
    
    img = Image.open(input_file_path)
    img.resize((800, 800), Image.ANTIALIAS)
    
    utility.make_directory(output_file_path)
    img.save(output_file_path)

def _create_image_info(input_file_path, output_file_path):
    from PIL import Image
    from PIL.ExifTags import TAGS
    
    img = Image.open(input_file_path)
    exif_dict = img._getexif()
    
    exif_result_info = {}
    for tag_id, value in exif_dict.items():
        tag = TAGS.get(tag_id, tag_id)
        if isinstance(value, bytes):
            continue
        exif_result_info[tag] = value
    # print(tag_dict)
    """
    exif_result_info = {}
    for k, v in exif_dict.items():
        tag_value = jpeg_tag_dict.get(k, None)
        if tag_value:
            tag_name = tag_value[0]
            exif_result_info[tag_name] = v
    """

    utility.make_directory(output_file_path)
    write_data = json.dumps(exif_result_info, cls=JsonEncoder, indent="  ", )
    with open(output_file_path, "w") as fp:
        fp.write(write_data)
    
    # pprint.pprint(exif_dict)
    # execute.arw_convert(input_file_path, output_file_path)

def _create_movie_small(size, bv, ba, input_file_path, output_file_path):

    if os.path.isfile(output_file_path):
        return

    utility.make_directory(output_file_path)

    command = (cf.FFMPEG_PATH, "-y", "-i", input_file_path,
               "-movflags", "faststart",
               "-c:v", "libx264", # libx265 # libx264 # mpeg2 # libxvid
               "-vf", "scale={}:-1".format(size),
                "-b:v", bv,
                "-c:a", "aac",
                # "-acodec aac -strict experimental"
                "-b:a", ba,
               output_file_path)
    print(command)
    
    def call_back(returncode, stdout_message):
        print(returncode, stdout_message)
        pass
    
    utility.create_process(command, call_back, 1, 2400)()

def _create_movie_thumbnail(input_file_path, output_file_path):

    if os.path.isdir(os.path.dirname(output_file_path)):
        return
        
    utility.make_directory(output_file_path)
    
    command = (cf.FFMPEG_PATH, "-y", "-i", input_file_path, "-vf",  "fps=1/10,scale=480:-1", output_file_path)
    print(command)
    
    def call_back(returncode, stdout_message):
        print(returncode, stdout_message)
        pass
    
    utility.create_process(command, call_back, 1, 20)()

def _create_info_file(file_info_list_by_date, cls):

    output_file_path = os.path.join(WEB_ROOT_PATH, INFO_FILE_NAME)
    
    utility.make_directory(output_file_path)
    date_list = [FolderInfo(v) for v, _ in file_info_list_by_date.items()]
    write_data = json.dumps(date_list, cls=JsonEncoder, indent="  ", )
    with open(output_file_path, "w") as fp:
        fp.write(write_data)

    for one_day, file_info_list in file_info_list_by_date.items():

        output_file_path = os.path.join(WEB_ROOT_PATH, one_day, cls.get_directory_name(), INFO_FILE_NAME)
        utility.make_directory(output_file_path)
        write_data = json.dumps(file_info_list, cls=JsonEncoder, indent="  ",)
        with open(output_file_path, "w") as fp:
            fp.write(write_data)

    for root, dirs, files in os.walk(WEB_ROOT_PATH):
        if not dirs:
            continue
        folder_list = [FolderInfo(os.path.basename(v)) for v in dirs]
        write_data = json.dumps(folder_list, cls=JsonEncoder, indent="  ",)
        with open(os.path.join(root, INFO_FILE_NAME), "w") as fp:
            fp.write(write_data)


def _create_file_info_list(input_path_list, ext_list, cls):
    
    file_path_list_list = []
    for input_path in input_path_list:
        file_path_list_list.append(utility.directory_walk(input_path, ext_list, None, 1))
        
    file_path_list = itertools.chain.from_iterable(file_path_list_list)
    
    file_info_list = []
    
    for file_path in file_path_list:
        dt = datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)
        print(file_path, dt.strftime('%Y%m%d%H%M'))
        file_info_list.append(cls(dt, file_path))
        
    sorted_file_info_list = sorted(file_info_list, key=lambda v:v.dt)
    
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
    _create_info_file(temp_image, ImageFileInfo)
    
    temp_movie = _create_file_info_list(cf.MOVIE_INPUT_PATH_LIST, (".MP4", ".mp4"), MovieFileInfo) # (".MP4", ".mp4")
    _create_info_file(temp_movie, MovieFileInfo)
    
    # pprint.pprint(file_info_list_by_date)
    if IS_CREATE_REF:
        _create_image_ref_data_execute(temp_image)
        _create_movie_ref_data_execute(temp_movie)
        
        # __create_ref_data_execute(temp_movie)
    # print(file_list)
    


if __name__ == "__main__":
    main()