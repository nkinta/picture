
from __future__ import print_function

import os
import struct

import utility
import define

source_directory = ""
target_directory = ""

SOI_TAG = 0xffd8
EXIF_TAG = 0xffe1
JFIF_TAG = 0xffe0

READ_SIZE = 256
DATA_SIZE = 1
MAX_JPEG_DATA = 2

ENDIAN_TYPE = {0x4d4d: ">", 0x4949: "<"}

def log(*args, **kwaargs):
    pass
    # print(*args, **kwaargs)

class Error(Exception):
    pass

class AppSegmentData(object):
    
    def __init__(self):
        # self.ifd_data_list = ifd_data_list
        # self.data = ""
        self.segment_tag = None
        self.segment_size = None

    def read_segment_header(self, f, ep):
        
        log("telld-> %04X" % f.tell())
        self.segment_tag, self.segment_size = data_read_one("HH", f, ep)
        log("%08X %04X %04X" % (f.tell(), self.segment_tag, self.segment_size))
        if self.segment_tag == EXIF_TAG:
            log("exif")
            exif_recognize = data_read_one("6c", f, ep)
            app_offset = f.tell()
            self.read_data(f, ep, app_offset)
    
        elif self.segment_tag == JFIF_TAG:
            log("jfif")
        
    def get_info(self):
        return self.segment_tag, self.segment_size
        
    def write_segment_header(self, f, ep, byte_order):

        data = struct.pack("%sH" % ep, EXIF_TAG) # app1
        f.write(data)
        size_pointer = f.tell()
        data = struct.pack("%sH" % ep, 0)  # todo:
        f.write(data)
        data = struct.pack("%s6s" % ep, b"Exif\0\0")
        f.write(data)
        app_offset = f.tell()
        unknown_data = 0x002a
        ifd_offset = 0x0008
        data = struct.pack("%sHHL" % ep, byte_order, unknown_data, ifd_offset)
        f.write(data)

        self.write_data(f, ep, app_offset)
        
        now = f.tell()
        try:
            f.seek(size_pointer)
            data = struct.pack("%sH" % ep, now - size_pointer)
            f.write(data)
        finally:
            f.seek(now)
        
    def read_data(self, f, ep, app_offset):
        # next_pointer_offset, ifd_data_list = read_ifd_data(f, ep, app_offset, self.ifd_data_list)
        
        byte_order, unknown_data, ifd_offset = data_read_one("HHL", f, ep)
        log("endian -> %04X" % byte_order, "ifd_offset -> %04X" % ifd_offset)
        ep = (ENDIAN_TYPE[byte_order])
        # self.read_ifd_data_all(f, new_ep, app_offset)
        
        app_segment_data_list = []
        next_pointer = f.tell()
        while True:
            log("next_pointer %08X" % next_pointer)
            f.seek(next_pointer)
            next_pointer_offset, ifd_data_list = read_ifd_data(f, ep, app_offset)
            app_segment_data_list.append(ifd_data_list)
            next_pointer = next_pointer_offset + app_offset
            if next_pointer_offset == 0:
                break
        
        self.ifd_data_list_list = app_segment_data_list


    def write_data(self, f, ep, app_offset):
        offset_pointer = None
        for ifd_data_list in self.ifd_data_list_list:
            if offset_pointer:
                now = f.tell()
                try:
                    f.seek(offset_pointer)
                    data = struct.pack("%sI" % ep, now - app_offset)
                    f.write(data)
                finally:
                    f.seek(now)
            offset_pointer = write_ifd_data(f, ep, app_offset, ifd_data_list)


class ExifData(object):
    
    def __init__(self, app_segment_data_list):
        self.app_segment_data_list = app_segment_data_list

def convert_int_to_data(ep, tag_type, count, v):
    struct_data = define.data_struct_dict[tag_type] * count
    v_string_temp = struct.pack("%sI" % ep, v)
    v_string = v_string_temp[0: struct.calcsize(struct_data)]
    result = struct.unpack("%s%s" % (ep, struct_data), v_string)
    return result
    
def convert_data_to_int(ep, tag_type, count, v):
    struct_data = define.data_struct_dict[tag_type] * count
    v_string_temp = struct.pack("%s%s" % (ep, struct_data), *v)
    v_string = v_string_temp.ljust(4, b"\x00")
    result = struct.unpack("%sI" % ep, v_string)[0]
    return result

class IfdData(object):
    
    def __init__(self, tag_id, tag_type, ifd_count, ifd_offset):
        self.tag_id = tag_id
        self.tag_type = tag_type
        self.ifd_count = ifd_count
        self.ifd_offset = ifd_offset
        
        self.tag_name = define.tag_id_to_name_dict.get(tag_id, ("Unknown",))[0]
        # log(tag_id, tag_type, ifd_count, ifd_offset)
        self.data_type_name = define.data_type_dict[tag_type]
        total_size = define.data_type_size_dict[tag_type] * ifd_count

        if total_size > 4:
            self.pointer_flag = True
        else:
            self.pointer_flag = False
            
        if self.pointer_flag:
            self.pm = "*"
        else:
            self.pm = ""

    def get_data(self, ep):
        if self.pointer_flag:
            ifd_offset = self.ifd_offset
        else:
            if self.tag_id == define.tag_name_to_id_dict["Exif_IFD_Pointer"][0]:
                ifd_offset = self.ifd_offset
            else:
                ifd_offset = convert_data_to_int(ep, self.tag_type, self.ifd_count, self.main_data)

        return (self.tag_id, self.tag_type, self.ifd_count, ifd_offset)

    def set_main_data(self, f, ep, app_offset):

        self.main_data = None
        self.unkown_data_flag = False
        if self.pointer_flag:

            if self.tag_id == define.tag_name_to_id_dict["MakerNote"][0]:
                self.unkown_data_flag = True
            else:
                now = f.tell()
                try:
                    f.seek(self.ifd_offset + app_offset)
        
                    struct_data = define.data_struct_dict[self.tag_type] * self.ifd_count
                    
                    temp_data = data_read_one(struct_data, f, ep)
                    if temp_data:
                        self.main_data = temp_data
                    else:
                        self.unkown_data_flag = True
                finally:
                    f.seek(now)
        else:
            self.main_data = convert_int_to_data(ep, self.tag_type, self.ifd_count, self.ifd_offset)
            
            if self.tag_id == define.tag_name_to_id_dict["Exif_IFD_Pointer"][0]:
                self.main_data = []
                now = f.tell()
                try:
                    # self.exif_pointer = 
                    f.seek(self.ifd_offset)
                    next_pointer = f.tell()
                    while next_pointer != 0:
                        f.seek(next_pointer + app_offset)
                        next_pointer, ifd_data_list = read_ifd_data(f, ep, app_offset)
                        self.main_data.append(ifd_data_list)

                    """
                    for temp in ifd_data_generater(f, ep):
                        # log(temp)
                        self.main_data.append(temp)
                    """
                finally:
                    f.seek(now)


    def __str__(self):
        return "%s %04X %s %03d %s%08X %s" % (self.tag_name,
                                           self.tag_id,
                                           self.data_type_name,
                                           self.ifd_count,
                                           self.pm,
                                           self.ifd_offset,
                                           self.main_data,
                                           )
                
        

def data_read_one(fmt, f, ep):
    temp_fmt = ("%s%s" % (ep, fmt))
    read_size = struct.calcsize(temp_fmt)
    data = f.read(read_size)
    if read_size > 256:
        return None
    return struct.unpack(temp_fmt, data)

def data_write_one(fmt, f, ep, data):
    temp_fmt = ("%s%s" % (ep, fmt))
    data = struct.pack(temp_fmt, data)
    f.write(data)

def write_ifd_data(f, ep, app_offset, ifd_data_list):
    
    valid_ifd_data_list = []
    for ifd_data in ifd_data_list:
        if ifd_data.main_data is None:
            continue
        elif ifd_data.tag_id == define.tag_name_to_id_dict["JPEGInterchangeFormat"][0]:
            continue
        elif ifd_data.tag_id == define.tag_name_to_id_dict["JPEGInterchangeFormatLength"][0]:
            continue

        valid_ifd_data_list.append(ifd_data)
        
    ifd_offset_tell_list = []
    data = struct.pack("%sH" % ep, len(valid_ifd_data_list))
    f.write(data)
    for ifd_data in valid_ifd_data_list:
        tag_id, tag_type, ifd_count, ifd_offset = ifd_data.get_data(ep)
        data = struct.pack("%sHHI" % ep, tag_id, tag_type, ifd_count)
        f.write(data)
        if ifd_data.pointer_flag:
            ifd_offset_tell_list.append(f.tell())
        elif ifd_data.tag_id == define.tag_name_to_id_dict["Exif_IFD_Pointer"][0]:
            ifd_offset_tell_list.append(f.tell())
        data = struct.pack("%sI" % ep, ifd_offset)
        f.write(data)

    offset_pointer = f.tell()
    next_ifd_offset = 0
    data = struct.pack("%sI" % ep, next_ifd_offset)
    f.write(data)
    
    offset_list = []
    for ifd_data in valid_ifd_data_list:
        tag_id, tag_type, ifd_count, ifd_offset = ifd_data.get_data(ep)
        main_data = ifd_data.main_data
        if ifd_data.pointer_flag:
            offset_list.append(f.tell() - app_offset)
            data = struct.pack("%s%s" % (ep, define.data_struct_dict[tag_type] * ifd_count), *main_data)
            f.write(data)
        elif ifd_data.tag_id == define.tag_name_to_id_dict["Exif_IFD_Pointer"][0]:
            offset_list.append(f.tell() - app_offset)
            for temp_ifd_data_list in ifd_data.main_data:
                write_ifd_data(f, ep, app_offset, temp_ifd_data_list)
                # f.write(data)
                # todo Ifd offset
    
    now = f.tell()
    try:
        for i, ifd_offset_tell in enumerate(ifd_offset_tell_list):
            f.seek(ifd_offset_tell)
            f.write(struct.pack("%sI" % ep, offset_list[i]))
    finally:
        f.seek(now)

    return offset_pointer

# ifd
def read_ifd_data(f, ep, app_offset):
    # data = f.read(2)
    # log(ep, data)
    (ifd_count,) = data_read_one("H", f, ep)
    log("ifd count -> %d" % ifd_count)

    ifd_data_list = []
    for i in range(ifd_count):
        now = f.tell()
        tag_id, type_id, ifd_count, ifd_offset = data_read_one("HHII", f, ep)
        # log("tell %08X" % f.tell())
        ifd_data = IfdData(tag_id, type_id, ifd_count, ifd_offset)
        ifd_data.set_main_data(f, ep, app_offset)
        ifd_data_list.append(ifd_data)
        log("%02d, %08X : %s" % (i, now, str(ifd_data)))
        
    (next_pointer_offset,) = data_read_one("I", f, ep)
    return next_pointer_offset, ifd_data_list


def read_arw(input_file_path):
    byte_order = 0x4d4d
    with open(input_file_path, "rb") as f:

        # byte_order, unknown_data, ifd_offset = data_read_one("HHL", f, ep)
        # log("endian -> %04X" % byte_order, "ifd_offset -> %04X" % ifd_offset)
        app_offset = 0
        ep = (ENDIAN_TYPE[byte_order])
        app_segment_data = AppSegmentData()
        app_segment_data.read_data(f, ep, app_offset)
        
        jpeg_info_list = []
        
        for ifd_data_list in app_segment_data.ifd_data_list_list:
            jpeg_main_pointer, jpeg_main_size = (None, None,)
            for ifd_data in ifd_data_list:
                if ifd_data.tag_id == define.tag_name_to_id_dict["JPEGInterchangeFormat"][0]:
                    jpeg_main_pointer = ifd_data.main_data[0]
                elif ifd_data.tag_id == define.tag_name_to_id_dict["JPEGInterchangeFormatLength"][0]:
                    jpeg_main_size = ifd_data.main_data[0]

            jpeg_info_list.append((jpeg_main_pointer, jpeg_main_size,))
        
        jpeg_data_list = []
        start_offset = 2
        for jpeg_info in jpeg_info_list:
            f.seek(jpeg_info[0] + start_offset)
            jpeg_data = f.read(jpeg_info[1] - start_offset)
            jpeg_data_list.append(jpeg_data)
        
        # app_segment_data_list = read_ifd_data_all(f, ep, 0)
        # exif_data = ExifData(app_segment_data_list)

    return app_segment_data, jpeg_data_list

def read_jpeg(input_file_path):
    ep = ">"
    ifd_data_list_list = []
    with open(input_file_path, "rb") as f:
        (soi_data,) = data_read_one("H", f, ep)
        log("%04X" % soi_data)
        if not soi_data == SOI_TAG:
            raise Error("no jpeg")
        
        while f.tell() < 0x10000:
            log("tell-> %04X" % f.tell())
            first_pointer = f.tell()
            app_segment_data = AppSegmentData()
            app_segment_data.read_segment_header(f, ep)
            segment_tag, segment_size = app_segment_data.get_info()
            log("segment_size %08X" % segment_size)
            next_pointer = first_pointer + 2 + segment_size
            log("nexp %08X" % next_pointer)
            f.seek(next_pointer)

def write_jpeg(app_segment_data, jpeg_data_list, output_file_path):
    # ep = ">"
    byte_order = 0x4d4d
    ep = ENDIAN_TYPE[byte_order]

    utility.make_directory(output_file_path)
    with open(output_file_path, "wb") as f:
        data = struct.pack("%sH" % ep, SOI_TAG)
        f.write(data)
        app_segment_data.write_segment_header(f, ep, byte_order)
        for jpeg_data in jpeg_data_list:
            f.write(jpeg_data)
        # Todo


def arw_convert(input_file_path, output_file_path):
    exif_data, jpeg_data_list = read_arw(input_file_path)
    write_jpeg(exif_data, jpeg_data_list, output_file_path)
    read_jpeg(output_file_path)
    
def jpg_convert(input_file_path, output_file_path):
    from PIL import Image
    from PIL import ExifTags

    if os.path.isfile(output_file_path):
        return

    print("{} -> {}".format(input_file_path, output_file_path))

    img = Image.open(input_file_path)
    new_img = img.resize((1620, 1080), Image.ANTIALIAS)

    utility.make_directory(output_file_path)
    new_img.save(output_file_path, quality=95)


def arw_read_test():
    input_file_path = os.path.join("F:\picture", "sample", "input", "DSC07476.ARW")
    output_file_path = os.path.join("F:\picture", "sample", "input", "DSC07479.jpg")
    exif_data, jpeg_data_list = read_arw(input_file_path)
    write_jpeg(exif_data, jpeg_data_list, output_file_path)
    read_jpeg(output_file_path)

def jpeg_read_test():
    # input_file_path = os.path.join("D:\picture", "sample", "input", "IMG_0737.JPG")
    # input_file_path = os.path.join("D:\picture", "sample", "input", "DSC02574.jpg")
    input_file_path = os.path.join("F:\picture", "sample", "input", "P1000253.JPG")
    read_jpeg(input_file_path)


def all_execute(input_directory_path, output_directory_path):
    
    pass_already_exist_flag = True
    new_ext = ".jpg"
    
    input_file_path_list = utility.directory_walk(input_directory_path,
                                                  [".ARW", ".arw", ".JPG", ".jpg"],
                                                  filtering = r".*(?<=\\)DSC[0-9]{5}\.")
    log(input_file_path_list)

    for input_file_path in input_file_path_list:
        temp_output_file_path = os.path.join(output_directory_path, os.path.relpath(input_file_path, input_directory_path))
        splited_tuple = os.path.splitext(temp_output_file_path)
        output_file_path = "%s%s" % (splited_tuple[0], new_ext)
        
        if pass_already_exist_flag:
            if os.path.isfile(output_file_path) == True:
                log("pass %s" % output_file_path)
                continue
        
        directory, file = os.path.split(output_file_path)
        if os.path.isdir(directory) == False:
            os.makedirs(directory)
        print("convert (%s) -> (%s)" % (input_file_path, output_file_path))
        old_ext = splited_tuple[1]
        if (old_ext.lower() == ".arw"):
            arw_convert(input_file_path, output_file_path)
        elif (old_ext.lower() == ".jpg"):
            jpg_convert(input_file_path, output_file_path)
        

def main():
    # jpeg_read_test()
    # arw_read_test()
    # one_file_test()                                                                                                    
    
    # input_directory_path = os.path.join("O:\picture", "pentax")
    input_directory_path = os.path.join("M:\picture", "strage")
    output_directory_path = os.path.join("M:\picture", "upload")
    all_execute(input_directory_path, output_directory_path)
    print("end")


if __name__ == "__main__":
    main()