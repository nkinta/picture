
from __future__ import print_function

import os
import http.server
import flask
import jinja2
import json
import config as cf

ROOT_PATH = os.path.join(cf.OUTPUT_PATH, "web_root")
INFO_FILE_NAME = "info.json"

class Error(Exception):
    pass


def all_execute(input_directory_path, output_directory_path):
    
    pass


app = flask.Flask(__name__)

# jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(r"C:/Users/nkinta/Documents/git/picture/picture_webserver/templates",  encoding='utf8'))
# template = jinja2_env.get_template("index.html")
# os.environ["FLASK_DEBUG"] = "1"

def _get_info_data(relative_path="./"):
    info_path = os.path.join(ROOT_PATH, relative_path, INFO_FILE_NAME)

    with open(info_path, "r") as fp:
        read_data = fp.read()
        
    data = json.loads(read_data)
    return data

def _get_data(data_children, child_name_list):
    parent_path = ""
    print(child_name_list)
    for child_name in child_name_list:
        print(child_name)
        path_dict = dict([(v["name"], v) for v in data_children])
        data = path_dict.get(child_name, None)
        if data is None:
            flask.abort(404)
        children_path = data.get("children_info_path", None)
        if children_path:
            child_dict = path_dict.get(child_name, None)
            if child_dict is None:
                flask.abort(404)
            
            path = os.path.join(parent_path, child_dict["children_info_path"])
            data_children = _get_info_data(path.replace("/", "\\"))
            parent_path = path
        else:
            data_children = path_dict[child_name].get("children", None)

    return data, data_children


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


@app.route("/")
def root_folder():
    
    data = _get_info_data()

    text = flask.render_template("directory_index.html", data_list=data)
    return text

@app.route("/<child_name1>/")
def child_folder1(child_name1):
    
    root_data = _get_info_data()
    _, data_children = _get_data(root_data, [child_name1])

    text = flask.render_template("directory_index.html", data_list=data_children)
    
    return text

@app.route("/<child_name1>/<child_name2>/")
def child_folder2(child_name1, child_name2):
    
    root_data = _get_info_data()
    data, data_children = _get_data(root_data, [child_name1, child_name2])

    """
    for i, root_child in enumerate(root_data):
        name = root_child["name"]
        if name == child_name1:
            prev = 
            
    print("data_children-", data_children)
    """

    
    index = {v["name"]: i for i, v in enumerate(root_data)}[child_name1]
    root_data_dict = {i : v["name"] for i, v in enumerate(root_data)} 
    
    prev_name = root_data_dict.get(index - 1, None)
    next_name = root_data_dict.get(index + 1, None)
    
    _add_info_for_web_all(child_name2, data_children)
    text = flask.render_template("{}_index_test.html".format(child_name2), data_list=data_children, prev=prev_name, next=next_name)
    
    return text


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/<child_name1>/<child_name2>/<child_name3>/<child_name4>/<path:filename>")
def child_data(child_name1, child_name2, child_name3, child_name4, filename):
    
    root_data = _get_info_data()
    data, _ = _get_data(root_data, [child_name1, child_name2, child_name3, child_name4])

    """
    path_dict = dict([(v["name"], v) for v in data])
    key = os.path.splitext(filename)[0]
    data = path_dict[key]
    """

    local_path = data["local_path"]
    mimetype = data["mimetype"] # ("mimetype", None)
    attachment = data.get("attachment", False) # ("mimetype", None)

    directory_path = os.path.dirname(local_path)
    basename = os.path.basename(local_path)
    
    print("mimetype", mimetype)
    
    download_file_info = flask.send_from_directory(directory_path, "{}".format(basename), mimetype=mimetype, as_attachment=attachment) # , as_attachment=True)
    
    return  download_file_info


def main():
    app.run(host="0.0.0.0", threaded=True, port=8080) # port=8080
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