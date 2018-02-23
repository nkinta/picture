
from __future__ import print_function

from picture_webserver import make_list

import socket
host = socket.gethostname()
print("picture_webserver.config_{}".format(host.lower()))
cf = __import__("config_{}".format(host.lower()))


def main():

    make_list.toggle_process()

    # __create_ref_data_execute(temp_movie)
    # print(file_list)


if __name__ == "__main__":
    main()
