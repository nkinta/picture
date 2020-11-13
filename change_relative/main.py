# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import utility
import re
import pprint
import jinja2

import numpy as np


class CncCommand(object):

    def __init__(self):
        self.pos = np.array([np.nan, np.nan, np.nan])
        self.main_command = ""
        self.original_line = ""
        self.suffix = ""

    def __str__(self):
        return "{}, {}".format(str(self.main_command), str(self.num))

ABS_MODE = "G90"
REL_MODE = "G91"

MAIN_POS_COMMAND = ("G0", "G1", "G2", "G3")


def to_pos_string(current_pos, diff_pos, mode):

    temp_pos_str_list = []
    xyz_str = ["X", "Y", "Z"]
    for index in range(len(xyz_str)):
        if (diff_pos[index] == 0):
            continue

        if mode is ABS_MODE:
            pos = current_pos[index]
        elif mode is REL_MODE:
            pos = diff_pos[index]

        pos_str = "{}{:.4g}".format(xyz_str[index], pos)
        temp_pos_str_list.append(pos_str)

    return " ".join(temp_pos_str_list)


def get_command(input_file_path, output_file_path):

    with open(input_file_path, mode="r") as f:
        lines = f.readlines()
    float_matching = r"[+-]?\d+(?:\.\d+)?"

    prog_command = re.compile(r"(G[0-9][0-9]?)(.*)")

    prog_search_xyz = re.compile(r"(([XYZ])({}))".format(float_matching))

    prog_suffix = re.compile(r"(?:[XYZ]{}\s*)+(.*)".format(float_matching))

    first_command = CncCommand()
    first_command.main_command = "G0"
    first_command.pos = np.array([0.0, 0.0, 0.0])
    command_list = []

    for line in lines:
        result_line = line
        m = prog_command.match(line)
        temp_command = None
        if m:
            command = m.group(1)
            temp_command = CncCommand()
            temp_command.original_line = result_line
            temp_command.main_command = command
            if command in MAIN_POS_COMMAND:
                # print(m.group(1))

                xyz_line = m.group(2)
                m_xyz_list = prog_search_xyz.findall(xyz_line)

                for m_xyz in m_xyz_list:
                    # print(m_xyz[1], m_xyz[2])
                    if "X" == m_xyz[1]:
                        temp_command.pos[0] = float(m_xyz[2])
                    elif "Y" == m_xyz[1]:
                        temp_command.pos[1] = float(m_xyz[2])
                    elif "Z" == m_xyz[1]:
                        temp_command.pos[2] = float(m_xyz[2])

                m_suffix = prog_suffix.search(xyz_line)

                if m_suffix:
                    temp_command.suffix = m_suffix.group(1)

        if temp_command:
            command_list.append(temp_command)
        else:
            command_list.append(result_line)

    return command_list


def get_cnc_line(command_list, mode, offset_pos, scale, replace_command_list):

    current_pos = np.array([np.nan, np.nan, np.nan])
    current_mode = ""

    first_line_0 = "G90\n"

    result_lines = [first_line_0]
    for temp_command in command_list:
        if isinstance(temp_command, CncCommand):

            result_line = None

            if temp_command.main_command == REL_MODE:
                current_mode = REL_MODE
            elif temp_command.main_command == ABS_MODE:
                current_mode = ABS_MODE
            elif temp_command.main_command in MAIN_POS_COMMAND:
                old_pos = current_pos.copy()
                if current_mode == ABS_MODE:
                    for index in range(len(current_pos)):
                        if np.isnan(temp_command.pos[index]):
                            continue
                        current_pos[index] = temp_command.pos[index]

                diff_pos = current_pos - old_pos

                print(current_pos, old_pos)

                if scale is None:
                    target_scale = np.array([1.0, 1.0, 1.0])
                else:
                    target_scale = scale

                replaced_command_name = temp_command.main_command
                for replace_command in replace_command_list:
                    before, after = replace_command
                    if before == temp_command.main_command:
                        replaced_command_name = after
                        break

                result_line = "{} {} {}\n".format(replaced_command_name,
                                                  to_pos_string(current_pos * target_scale + offset_pos, diff_pos, mode),
                                                  temp_command.suffix)

            if result_line is None:
                result_line = temp_command.original_line

        elif isinstance(temp_command, str):
            result_line = temp_command

        result_lines.append(result_line)

    return result_lines


def template_change(template_line_list, data):
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(template_file_path), encoding='utf8'))
    template = env.get_template(os.path.basename(template_file_path))
    """

    template = jinja2.Template("".join(template_line_list))

    result_text = template.render(data)  # 辞書で指定する

    return result_text


def main_execute(input_file_path, output_file_path, mode, offset_pos, data, scale=None, replace_command_list=()):

    command_list = get_command(input_file_path, output_file_path)

    result_line_list = get_cnc_line(command_list, mode, offset_pos, scale, replace_command_list)

    if data:
        result_text = template_change(result_line_list, data)
    else:
        result_text = "".join(result_line_list)

    with open(output_file_path, mode="w") as f:
        f.write(result_text)


def gcode_import(input_file_path):

    with open(input_file_path, mode="r") as f:
        line_list = f.readlines()

    return line_list


def main2():

    input_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\tire", "tire_maru_only.nc")
    output_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\tire", "tire_maru_only_relative.nc")

    offset_pos = np.array([0.0, 0.0, 0.0])

    main_execute(input_file_path, output_file_path, REL_MODE, offset_pos, {})


def main():

    input_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\flex\bampercut", "sha_hole_front.nc")
    output_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\flex\bampercut", "sha_hole_front_flip.nc")

    offset_pos = np.array([0.0, 0.0, 0.0])
    scale = np.array([1.0, -1.0, 1.0])
    # hole = "\n".join(("G91 Z0 F40", "G1 Z-1 F1", "G4 P1", "G1 Z-4.8 F1", "G4 P1", "G1 Z2 F80"))
    # data = {'hole': hole}
    # data = None
    hole_template_file = os.path.join(r"D:\dropbox\Dropbox\cnc\spacer", "hole_template.nc")

    hole = "".join(gcode_import(hole_template_file))
    data = {'hole': hole}

    main_execute(input_file_path, output_file_path, ABS_MODE, offset_pos, data, scale, [("G3", "G2"), ("G2", "G3")])


def main4():

    input_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\jigu_carbon", "bar_hole_4mm_2mm_drill_4_template_newhole_only.nc")
    output_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\jigu_carbon", "bar_hole_4mm_2mm_drill_4_result_newhole_only.nc")

    offset_pos = np.array([0.0, 0.0, 0.0])
    scale = np.array([1.0, 1.0, 1.0])
    # hole = "\n".join(("G91 Z0 F40", "G1 Z-1 F1", "G4 P1", "G1 Z-4.8 F1", "G4 P1", "G1 Z2 F80"))
    # data = {'hole': hole}
    # data = None
    hole_template_file = os.path.join(r"D:\dropbox\Dropbox\cnc\jigu_carbon", "hole_drill_template.nc")

    hole = "".join(gcode_import(hole_template_file))
    data = {'hole': hole}

    main_execute(input_file_path, output_file_path, ABS_MODE, offset_pos, data, scale)


def main3():

    input_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\chochin\no2", "bar_hole_4mm_2mm_drill_3_template.nc")
    output_file_path = os.path.join(r"D:\dropbox\Dropbox\cnc\chochin\no2", "bar_hole_4mm_2mm_drill_3_result.nc")

    offset_pos = np.array([0.0, -16.0, 0.0])

    # hole = "\n".join(("G1 Z0 F40", "G1 Z-1 F5", "G1 Z-4.8 F1", "G4 P3", "G1 Z2 F80"))
    # data = {'hole': hole}
    data = None

    main_execute(input_file_path, output_file_path, ABS_MODE, offset_pos, data)


if __name__ == "__main__":
    main2()
