
from __future__ import print_function

import os
import flask
import jinja2
import json

import datetime
import zipfile
import collections

from werkzeug.routing import BaseConverter

from picture_webserver.config import *

RESPONSE_PATH = os.path.join(cf.OUTPUT_PATH, "response_root")

INFO_FILE_NAME = "info.json"

DATE_REGEX = "<regex('20[0-9]{2}_[0-9]{4}'):date_uri>"
MEDIA_TYPE_REGEX = "<regex('(?:(?:images)|(?:movies))'):media_type_uri>"
MEDIA_DATA_REGEX = "<regex('(?:(?:DSC[0-9]{5})|(?:C[0-9]{4})|(?:GH[0-9]{6})|(?:MAH[0-9]{5}))'):media_data_uri>"
MEDIA_DATA_TYPE_REGEX = "<media_data_type_uri>"
DOWNLOAD_FILE_REGEX = "<download_file_uri>"

ROOT_PATH_LIST = [(cf.WEB_ROOT_PATH, "main"), (cf.FAV_ROOT_PATH, "fav"), (cf.ACCESS_ROOT_PATH, "access")]


class Error(Exception):
    pass


def all_execute(input_directory_path, output_directory_path):

    pass


class RegexConverter(BaseConverter):

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = flask.Flask(__name__)
app.url_map.converters['regex'] = RegexConverter


# jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(r"C:/Users/nkinta/Documents/git/picture/picture_webserver/templates",  encoding='utf8'))
# template = jinja2_env.get_template("index.html")
# os.environ["FLASK_DEBUG"] = "1"

FILE_CACHE_DICT = {}


def _get_info_data(root_path=cf.WEB_ROOT_PATH, relative_path="./"):
    info_path = os.path.join(root_path, relative_path.replace("/", os.path.sep), INFO_FILE_NAME)

    norm_path = os.path.normpath(info_path)

    # read from cache
    data = FILE_CACHE_DICT.get(norm_path, None)
    if data:
        return data

    with open(norm_path, "r") as fp:
        read_data = fp.read()

    data = json.loads(read_data)

    # cache
    FILE_CACHE_DICT[norm_path] = data

    return data


def _get_serialize_func(relative_path, data_children, root_path):
    def temp_func():
        write_data = json.dumps(data_children, indent="  ", )
        with open(os.path.join(root_path, relative_path.replace("/", os.path.sep), INFO_FILE_NAME), "w") as fp:
            fp.write(write_data)
    return temp_func


def _get_and_combine_data(child_name_list):

    combine_list = []
    for root_path, tag in ROOT_PATH_LIST:
        result = _get_data(child_name_list, root_path)
        if result:
            data, data_children, _ = result
            combine_list.append((tag, data, data_children))

    result_data, result_data_children = _combine_data_children(combine_list)

    return result_data, result_data_children


def _get_data(child_name_list, root_path=cf.WEB_ROOT_PATH):

    data = None
    parent_path = root_path
    data_children = _get_info_data(root_path)
    serialize_func = _get_serialize_func(parent_path, data_children, root_path)

    for child_name in child_name_list:
        print(child_name)
        path_dict = dict([(v["name"], v) for v in data_children])
        data = path_dict.get(child_name, None)
        serialize_func = _get_serialize_func(parent_path, data_children, root_path)

        if data is None:
            if root_path is cf.WEB_ROOT_PATH:
                flask.abort(404)
            else:
                return None
        children_path = data.get("children_info_path", None)
        if children_path:
            child_dict = path_dict.get(child_name, None)
            if child_dict is None:
                if root_path is cf.WEB_ROOT_PATH:
                    flask.abort(404)
                else:
                    return None

            path = os.path.join(parent_path, child_dict["children_info_path"])
            data_children = _get_info_data(root_path, path)

            parent_path = path
        else:
            data_children = path_dict[child_name].get("children", None)

    return data, data_children, serialize_func


def _add_info_for_web(data_type, data_list):
    print(data_list)
    data_info_dict = {v["name"]: v for v in data_list}

    if data_type == "images":
        data = data_info_dict["arw"]
        data["download_size"] = "{:,.0f}MB".format(data["size"] / 1000000)
    elif data_type == "movies":
        data = data_info_dict["movie"]
        data["download_size"] = "{:,.0f}MB".format(data["size"] / 1000000)

    return data_info_dict
    # print("movie_data - ", movie_data)


def _add_info_for_web_all(data_type, data_list):

    for data in data_list:
        children = data.get("children")
        if children is None:
            continue
        data["web"] = _add_info_for_web(data_type, children)


def _is_access(data):
    user = flask.request.args.get('user')
    if (user == "admin"):
        return True

    if data["access"].get("users", True) == True:
        return True
    else:
        return False


def _user_access_filtering(combined_data_children):
    combined_data_children = [v for v in combined_data_children if _is_access(v)]

    return combined_data_children


def _combine_data_children(data_children_list):

    def _combine_data(base_data, root_name, data):
        if base_data is None:
            return
        base_data[root_name] = data

    root_name, base_data, base_data_children = data_children_list[0]
    result = base_data, base_data_children
    if base_data_children is None:
        return result

    base_data_children_dict = {v["name"]: v for v in base_data_children}

    for root_name, data, data_children in data_children_list[1:]:
        _combine_data(base_data, root_name, data)

        data_children_dict = {v["name"]: v for v in data_children}
        for name, v in data_children_dict.items():
            if name in base_data_children_dict:
                _combine_data(base_data_children_dict[name], root_name, v)

    return result


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/".join(("", DATE_REGEX, MEDIA_TYPE_REGEX, MEDIA_DATA_REGEX, MEDIA_DATA_TYPE_REGEX, DOWNLOAD_FILE_REGEX)))
def child_data2(date_uri, media_type_uri, media_data_uri, media_data_type_uri, download_file_uri):

    data, _ = _get_and_combine_data([date_uri, media_type_uri, media_data_uri, media_data_type_uri])

    media_data, _ = _get_and_combine_data([date_uri, media_type_uri, media_data_uri])
    if not _is_access(media_data):
        flask.abort(404)

    # filtered_combined_data_children = _user_filtering(data_children)

    local_path = data["local_path"]
    mimetype = data["mimetype"]  # ("mimetype", None)
    attachment = data.get("attachment", False)  # ("mimetype", None)
    attachment_filename = data.get("attachment_filename", None)

    directory_path = os.path.dirname(local_path)
    basename = os.path.basename(local_path)

    print("mimetype", mimetype)

    download_file_info = flask.send_from_directory(directory_path, basename, mimetype=mimetype, as_attachment=attachment, attachment_filename=attachment_filename)  # , as_attachment=True)

    return download_file_info


@app.route("/".join(("", DATE_REGEX, MEDIA_TYPE_REGEX, MEDIA_DATA_REGEX, "")), methods=['PUT'])
def data_info_put(date_uri, media_type_uri, media_data_uri):

    # for v in (('favorite', cf.FAV_ROOT_PATH), ('users', cf.ACCESS_ROOT_PATH),):
    TEMP_DICT = {"fav": 'favorite', "access": 'users'}

    for v in ROOT_PATH_LIST[1:]:
        path, name = v
        key = TEMP_DICT[name]
        data, _, serialize_func = _get_data([date_uri, media_type_uri, media_data_uri], path)  # media_data_uri

        if key in flask.request.form:
            v = flask.request.form[key]
            data[key] = v

        serialize_func()

    return ""


@app.route("/".join(("", DATE_REGEX, MEDIA_TYPE_REGEX, DOWNLOAD_FILE_REGEX)))
def all_zip(date_uri, media_type_uri, download_file_uri):

    _, data_children = _get_and_combine_data([date_uri, media_type_uri])

    file_info_list = []
    for data_child in data_children:
        if not _is_access(data_child):
            continue
        target_data, _ = _get_and_combine_data([date_uri, media_type_uri, data_child["name"], os.path.splitext(download_file_uri)[0]])
        local_path = target_data["local_path"]
        attachment_filename = target_data["attachment_filename"]
        file_info_list.append((local_path, attachment_filename))

    common_directory_path = os.path.commonpath([v for v, _ in file_info_list])

    zip_file_path = os.path.join(common_directory_path, "{}_{}".format(media_type_uri, download_file_uri))
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, file_name in file_info_list:
            zf.write(file_path, arcname=file_name)

    # print("data_children", data_children)

    directory_path = os.path.dirname(zip_file_path)
    basename = os.path.basename(zip_file_path)

    mimetype = "application/zip"
    download_file_info = flask.send_from_directory(directory_path, basename, mimetype=mimetype, as_attachment=True)  # , as_attachment=True)

    return download_file_info


@app.route("/".join(("", DATE_REGEX, MEDIA_TYPE_REGEX, "")))
def child_folder2(date_uri, media_type_uri):

    _, data_children = _get_and_combine_data([date_uri, media_type_uri])

    _, root_data_children = _get_and_combine_data([])

    index = {v["name"]: i for i, v in enumerate(root_data_children)}[date_uri]
    root_data_dict = {i: v["name"] for i, v in enumerate(root_data_children)}

    prev_name = root_data_dict.get(index - 1, None)
    next_name = root_data_dict.get(index + 1, None)

    _add_info_for_web_all(media_type_uri, data_children)

    current_days = {"prev": prev_name, "current": date_uri, "next": next_name}

    inverse_media_type = {"images": "movies", "movies": "images"}[media_type_uri]

    filtered_combined_data_children = _user_access_filtering(data_children)

    text = flask.render_template("{}_index.html".format(media_type_uri),
                                 data_list=filtered_combined_data_children,
                                 current_days=current_days,
                                 media_type=media_type_uri,
                                 query_string=flask.request.query_string.decode(),
                                 user=flask.request.args.get("user", None),
                                 inverse_media_type=inverse_media_type,
                                 datetime=datetime.datetime.utcnow())

    return text


@app.route("/".join(("", DATE_REGEX, "")))
def child_folder1(date_uri):

    _, data_children = _get_and_combine_data([date_uri])

    text = flask.render_template("directory_index.html",
                                 data_list=data_children,
                                 datetime=datetime.datetime.utcnow())

    return text


@app.route("/")
def root_folder():

    data = _get_info_data()
    text = flask.render_template("directory_index.html",
                                 data_list=data,
                                 datetime=datetime.datetime.utcnow()
                                 )
    return text


def main():
    app.run(host="0.0.0.0", threaded=True, port=8080)  # port=8080
    # app.add_url_rule('/favicon.ico', redirect_to=flask.url_for('static', filename='favicon.ico'))

if __name__ == "__main__":
    main()

"""
def main():

    os.chdir(r"D:\movie_workspace")
    
    server_address = ("", 8000)
    handler_class = http.server.SimpleHTTPRequestHandler
    simple_server = http.server.HTTPServer(server_address, handler_class)
    simple_server.serve_forever()
"""

if __name__ == "__main__":
    main()
