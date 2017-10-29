
from __future__ import print_function

import os
import utility
import json
from PIL import Image
from PIL import ExifTags

import execute
from picture_webserver import config as cf

class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, "to_json"):
            return o.to_json()
       
        return json.JSONEncoder.default(self, o)


def create_image_jpg(input_file_path, output_file_path):
    
    if os.path.isfile(output_file_path):
        return

    print("{} -> {}".format(input_file_path, output_file_path))

    execute.arw_convert(input_file_path, output_file_path)


def create_image_small_jpg(input_file_path, output_file_path):

    if os.path.isfile(output_file_path):
        return
    
    print("{} -> {}".format(input_file_path, output_file_path))
    
    img = Image.open(input_file_path)
    img.thumbnail((160, 160), Image.ANTIALIAS)
    
    utility.make_directory(output_file_path)
    img.save(output_file_path)


def create_image_middle_jpg(input_file_path, output_file_path):
    
    if os.path.isfile(output_file_path):
        return
    
    print("{} -> {}".format(input_file_path, output_file_path))
    
    img = Image.open(input_file_path)
    img.resize((800, 800), Image.ANTIALIAS)
    
    utility.make_directory(output_file_path)
    img.save(output_file_path)

def create_image_info(input_file_path, output_file_path):

    if os.path.isfile(output_file_path):
        return
    
    print("{} -> {}".format(input_file_path, output_file_path))
    
    img = Image.open(input_file_path)
    exif_dict = img._getexif()
    
    exif_result_info = {}
    for tag_id, value in exif_dict.items():
        tag = ExifTags.TAGS.get(tag_id, tag_id)
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

