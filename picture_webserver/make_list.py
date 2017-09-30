
from __future__ import print_function

import os
import http.server
import datetime
import pprint
import utility
import json

import config as cf

THUMBNAIL_DEPOT = os.path.join(cf.OUTPUT_PATH, "thumbnail_depot")
WEB_ROOT_PATH = os.path.join(cf.OUTPUT_PATH, "web_root")

INFO_FILE_NAME = "info.json"

class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "to_json"):
            return o.to_json()
       
        return json.JSONEncoder.default(self, o)

#vJSON_ENCODER = json.JSONEncoder(default=json_enc_default)


class Error(Exception):
    pass

class FolderInfo():
    
    def __init__(self, date_name):
        self.name = date_name
        
    def get_path(self):
        return os.path.join(".", self.name)

    def to_json(self):
        result = {
            "name": self.name,
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "children_info_path": "{}/".format(self.get_path().replace("\\", "/")),
                  }
        return result

class FileInfo():
    
    def __init__(self, dt, local_path):
        self.dt = dt
        self.local_path = local_path
    
    def get_id(self):
        basename = self.get_name()
        dirname = os.path.basename(os.path.dirname(self.local_path))
        id = "{}_{}".format(dirname, basename)
        return id
    
    def get_path(self):
        return os.path.join(".", self.get_name())
    
    def get_name(self):
        name = os.path.basename(os.path.splitext(self.local_path)[0])
        return name
    
    def get_thumbnail_path(self):
        return os.path.join(self.get_id())
    
    def to_json(self):
        result = {
            # "id": self.get_id(),
            "name": self.get_name(),
            "path": "{}/".format(self.get_path().replace("\\", "/")),
            "time": self.dt.strftime('%Y%m%d%H%M'),
            "children": [
                {"name": "thumbnail",
                 "path": "thumbnail/",
                 "download_filename": "thumbnail_main.png",
                 "local_path": os.path.join(THUMBNAIL_DEPOT, self.get_thumbnail_path(), "img_001.png"),
                 },
                {"name": "mp4",
                 "path": "mp4/",
                 "download_filename": "movie.mp4",
                 "local_path": self.local_path,
                    },
            ]
        }
        return result
    
    def __repr__(self):
        return str(self.__dict__)


def get_one_day_directory_name(dt):
    one_day = (dt.year, dt.month, dt.day)
    directory_name = '{}_{:0>2}{:0>2}'.format(*one_day)
    return directory_name

def create_thumbnail_execute(file_info_list_by_date):
    
    for one_day, file_info_list in file_info_list_by_date.items():
        for file_info in file_info_list:
            # = file_info
            
            
            # output_file_path = os.path.join(THUMBNAIL_DEPOT, file_info.get_thumbnail_path(), "img_%03d.png")
            output_file_path = os.path.join(THUMBNAIL_DEPOT, file_info.get_thumbnail_path(), "small.mpg")
            
            directory = os.path.dirname(output_file_path)
            if os.path.isdir(directory) == False:
                os.makedirs(directory)
            # create_thumbnail_ffmpeg(file_info.local_path, output_file_path)
            __create_small(file_info.local_path, output_file_path)
            # return

def __create_thumbnail(input_file_path, output_file_path):
    
    # return
    
    command = (cf.FFMPEG_PATH, "-y", "-i", input_file_path, "-vf",  "fps=1/10,scale=192:-1", output_file_path)
    print(command)
    
    def call_back(returncode, stdout_message):
        print(returncode, stdout_message)
        pass
    
    utility.create_process(command, call_back, 1, 1200)()
    
def __create_small(input_file_path, output_file_path):

    return

    command = (cf.FFMPEG_PATH, "-y", "-i", input_file_path, "-vf",  "scale=240:-1", output_file_path)
    print(command)
    
    def call_back(returncode, stdout_message):
        print(returncode, stdout_message)
        pass
    
    utility.create_process(command, call_back, 1, 1200)()


def create_info_file(file_info_list_by_date):

    output_file_path = os.path.join(WEB_ROOT_PATH, INFO_FILE_NAME)
    utility.make_directory(output_file_path)
    with open(output_file_path, "w") as fp:
        date_list = [FolderInfo(v) for v, _ in file_info_list_by_date.items()]
        write_data = json.dumps(date_list, cls=JsonEncoder, indent="  ", )
        fp.write(write_data)

    for one_day, file_info_list in file_info_list_by_date.items():
        output_file_path = os.path.join(WEB_ROOT_PATH, one_day, INFO_FILE_NAME)
    
        utility.make_directory(output_file_path)

        write_data = json.dumps(file_info_list, cls=JsonEncoder, indent="  ",)
        with open(output_file_path, "w") as fp:
            fp.write(write_data)

def main():

    file_path_list = utility.directory_walk(cf.INPUT_PATH, (".MP4", ".mp4"), None, 1)
    
    file_info_list = []
    
    for file_path in file_path_list:
        dt = datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)
        print(file_path, dt.strftime('%Y%m%d%H%M'))
        file_info_list.append(FileInfo(dt, file_path))
        
    sorted_file_info_list = sorted(file_info_list, key=lambda v:v.dt)
    
    file_info_list_by_date = {}
    for file_info in sorted_file_info_list:
        dt = file_info.dt
        file_path = file_info.local_path
        one_day = get_one_day_directory_name(dt)
        file_list = file_info_list_by_date.get(one_day, None)
        if file_list is None:
            file_list = []
            file_info_list_by_date[one_day] = file_list
        
        file_list.append(file_info)
        
    create_info_file(file_info_list_by_date)
    
    # pprint.pprint(file_info_list_by_date)
    
    create_thumbnail_execute(file_info_list_by_date)
    # print(file_list)
    


if __name__ == "__main__":
    main()