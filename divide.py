
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

def data_read_one(fmt, f, ep):
    temp_fmt = ("%s%s" % (ep, fmt))
    read_size = struct.calcsize(temp_fmt)
    data = f.read(read_size)
    if read_size > 256:
        return None
    return struct.unpack(temp_fmt, data)

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
    with open(output_file_path, "wb") as f:
        data = struct.pack("%sH" % ep, SOI_TAG)
        f.write(data)
        app_segment_data.write_segment_header(f, ep, byte_order)
        for jpeg_data in jpeg_data_list:
            f.write(jpeg_data)
        # Todo

if __name__ == "__main__":
    main()