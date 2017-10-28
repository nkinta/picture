
from __future__ import print_function

import os
import utility

import config as cf


def create_movie_small(size, bv, ba, input_file_path, output_file_path):

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


def create_movie_thumbnail(input_file_path, output_file_path):

    if os.path.isdir(os.path.dirname(output_file_path)):
        return
        
    utility.make_directory(output_file_path)
    
    command = (cf.FFMPEG_PATH, "-y", "-i", input_file_path, "-vf",  "fps=1/10,scale=480:-1", output_file_path)
    print(command)
    
    def call_back(returncode, stdout_message):
        print(returncode, stdout_message)
        pass
    
    utility.create_process(command, call_back, 1, 20)()

