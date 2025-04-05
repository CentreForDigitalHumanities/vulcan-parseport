import os
from xml.etree import ElementTree


def create_frame_to_definition_dict(frames_path: str):
    frame_to_definition_text = dict()
    for filename in os.listdir(frames_path):
        if filename.endswith(".xml"):
            _process_xml(frames_path + filename, frame_to_definition_text)

    return frame_to_definition_text


def _process_xml(file_path, frame_to_definition_text):
    tree = ElementTree.parse(file_path)
    root = tree.getroot()
    frames_here = set()
    frame_to_short_def = dict()
    _get_and_store_definition_texts(frame_to_definition_text, frame_to_short_def, frames_here, root)
    _add_alternative_frames_to_definition_texts(frame_to_definition_text, frame_to_short_def, frames_here)


def _get_and_store_definition_texts(frame_to_definition_text, frame_to_short_def, frames_here, root):
    for predicate in root.findall("predicate"):
        for roleset in predicate:
            if "id" in roleset.attrib and "name" in roleset.attrib:
                definition_text, frame_name, short_definition = _get_frame_info(frames_here, roleset)
                frame_to_short_def[frame_name] = short_definition
                frame_to_definition_text[frame_name] = definition_text


def _get_frame_info(frames_here, roleset):
    short_definition = roleset.attrib["name"]
    frame_name = roleset.attrib["id"].replace(".", "-").replace("_", "-")
    definition_text = _get_definition_text(frame_name, frames_here, roleset, short_definition)
    return definition_text, frame_name, short_definition


def _get_definition_text(frame_name, frames_here, roleset, short_definition):
    definition_text = ""
    # print(roleset.tag, roleset.attrib)
    frames_here.add(frame_name)
    definition_text += frame_name + ": " + short_definition + "\n"
    definition_text = _add_roles_text(definition_text, roleset)
    return definition_text


def _add_roles_text(definition_text, roleset):
    roles = roleset.find("roles")
    if roles:
        for role in roles:
            if "n" in role.attrib.keys() and "descr" in role.attrib.keys():
                role_label = ":ARG" + role.attrib["n"]
                role_def = role.attrib["descr"]
                definition_text += "\t" + role_label + ": " + role_def + "\n"
    return definition_text


def _add_alternative_frames_to_definition_texts(frame_to_definition_text, frame_to_short_def, frames_here):
    for frame in frames_here:
        if len(frames_here) == 1:
            frame_to_definition_text[frame] += "\n(no alternative frames)"
        else:
            frame_to_definition_text[frame] += "\nAlternative frames:\n"
            for other_frame in [f for f in frames_here if f != frame]:
                frame_to_definition_text[frame] += other_frame + ": " + frame_to_short_def[other_frame] + "\n"
