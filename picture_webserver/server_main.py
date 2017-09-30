
from __future__ import print_function

import os
import http.server
import flask
import jinja2
import json

ROOT_PATH = r"D:\web_servert_test\web_root"
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
        data = path_dict[child_name]
        children_path = data.get("children_info_path", None)
        if children_path:
            path = os.path.join(parent_path, path_dict[child_name]["children_info_path"])
            data_children = _get_info_data(path.replace("/", "\\"))
        else:
            data_children = path_dict[child_name].get("children", None)

    return data, data_children

@app.route("/")
def root_folder():
    
    data = _get_info_data()

    text = flask.render_template("index.html", data_list=data)
    return text

@app.route("/<child_name1>/")
def child_folder1(child_name1):
    
    parent_data = _get_info_data()
    
    _, data_children = _get_data(parent_data, [child_name1])

    # template = jinja2_env.get_template("date_index.html")
    # text = template.render({"data_list": data})
    # template = jinja2_env.get_template("date_index.html")
    text = flask.render_template("date_index.html", data_list=data_children)
    
    return text

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/<child_name1>/<child_name2>/<child_name3>/<path:filename>")
def child_folder2(child_name1, child_name2, child_name3, filename):
    
    parent_data = _get_info_data()
    data, _ = _get_data(parent_data, [child_name1, child_name2, child_name3])

    """
    path_dict = dict([(v["name"], v) for v in data])
    key = os.path.splitext(filename)[0]
    data = path_dict[key]
    """

    local_path = data["local_path"]
    directory_path = os.path.dirname(local_path)
    basename = os.path.basename(local_path)
    
    print("local_path", local_path)
    
    download_file_info = flask.send_from_directory(directory_path, "{}".format(basename), as_attachment=True)
    
    return  download_file_info


def main():
    app.run(port=8080)
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