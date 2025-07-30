# Here is the place to but general helper functions

import ast
import json
from pathlib import Path
from pprint import pprint
from typing import List, Tuple
import toml
import pandas as pd

from ._backend_calls import _backend_POST, _backend_PUT, _backend_GET


def load_file(filename: Path) -> dict | pd.DataFrame:
    """
    Load data from a file. The function currently supports JSON files.

    Parameters:
    filename (Path): The path to the file.

    Returns:
    dict: The data loaded from the file if it's a JSON.
    """
    if filename.suffix == '.csv':
        df = pd.read_csv(filename, sep=',', header=0,
                         index_col=None, na_values=['NA', '?'])
        return df

    elif filename.suffix == '.json':
        with open(filename, 'r') as file:
            return json.load(file)

    elif filename.suffix == '.toml':
        with open(filename, 'r') as file:
            return toml.load(file)

    else:
        raise ValueError(
            "You need to add the file format to the load_file function.")



def create_new_project(project_info: dict):
    """Create a new project in the backend.
    Params:
        project_info(dict):
    Returns:
        dict:
    """
    status_code, message = _backend_POST(
        endpoint=f"/v2/projects/", data=project_info)
    if status_code == 200:
        return message
    else:
        print(f"Error creating project: {message}")
        return {"error": message}


def get_list_of_all_project_infos() -> list[tuple[int, str, str]]:
    """A function to connect to the backend and get a list of all projects
    in the current project data base.

    Params:
        None

    Retruns:
        all_project (list): List of tuples of id and name for all projects in the projectDB
        project_id (int): The project Identification Number
        project_name (str): The name of the project/mission
    """

    status_code, projects = _backend_GET(endpoint=f"/v2/projects/")
    project_ids: list[tuple[int, str, str]] = []
    if status_code == 200:
        for project in projects:
            project_ids.append((project["id"], project["project_name"], project["modified"]))
        return project_ids
    else:
        print(f"Error fetching projects: {projects}")
        return []

def get_project_info(project_id: int) -> dict:
    status_code, project_info = _backend_GET(endpoint=f"/v2/projects/{project_id}/")
    return project_info


def set_project_name(project_id: int, project_name: str) -> dict:
    """A function to set the project name of a specific project, identified by its ID.

    Params:
        project_id (int): The project Identification Number
        project_name(str): Name of the project/mission, eg OPS-Sat
    Returns:
        dict: html response from the backend to indicate success (200) or problems
    """

    data = {
        "project_id": project_id,
        "project_name": project_name,
    }

    # status, msg = _backend_put(endpoint=f"/v2/projects/{project_id}", data=data)
    # return (status, msg)
    status_code, msg = _backend_PUT(endpoint=f"/v2/projects/{project_id}/", data=data)
    if status_code == 200:
        return msg
    else:
        print(f"Error setting project name: {msg}")
        return {"error": msg}


def get_recent_project() -> tuple[int, str, str]:
    status_code, msg = _backend_GET(endpoint=f"/v2/projects/recent/")
    if status_code != 200:
        print(f"Error fetching recent project: {msg}")
        return (None, "No recent project found.")
    return (msg["id"], msg["project_name"], msg["modified"])


def get_mission_info(project_id: int) -> dict:
    """A function to get the mission/orbit info for a specific project based on its ID.
    Params:
        project_id (int): The project Identification Number

    Returns:
        dict: Keplerian elements to define the orbit
    """

    response = _backend_GET(
        endpoint=f"/v2/projects/{project_id}/mission/")
    return response["orbit"]


def set_mission_orbit(project_id: int, orbit_info: dict) -> dict:
    """A function to set the orbit in the project database.
    Params:
        project_id (int): The project Identification Number
        orbit_info(dict): Information about the satelllite's orbit
    Returns:
        dict: html response from the backend to indicate success (200) or problems
     """

    data = {
        "mission_name": "string",  # TODO remove?
        "description": "string",  # TODO remove?
        "launch_date": "string",
        "purpose": "string",  # TODO remove?
        "website": "string",  # TODO remove?
        "picture_web": "string",  # TODO remove?
        "project_id": 0,
        "orbit": orbit_info,
        # "orbit": {
        #     "celestial_object": "string",
        #     "orbit_shell": "string",
        #     "altitude_km": 0,
        #     "epoch_utc": "string",
        #     "semi_major_axis_km": 0,
        #     "eccentricity": 0,
        #     "inclination_degrees": 0,
        #     "perigee_height_km": 0,
        #     "apogee_height_km": 0,
        #     "raan_degrees": 0,
        #     "argument_of_perigee_degrees": 0,
        #     "mean_anomaly_at_epoch_degrees": 0,
        #     "revolutions_per_day": 0,
        #     "orbit_number_at_epoch": 0,
        #     "time_eclipse_min": 0,
        #     "mission_id": 0  # TODO remove?
        # }
    }

    # {
    #     "Celestical_Object": "Earth",  # Earth, Luna, Sun, Mars
    #     "Orbit_shell" : "LEO",  # LEO, MEO, GEO
    #     "Altitude_km" : 515,
    #     "Epoch_UTC" : datetime.strptime("2024-05-27T07:32:00", "%Y-%m-%dT%H:%M:%S"),
    #     "Semi_major_Axis_km" : 6_786,
    #     "Eccentricity" : 0.0005551,
    #     "Inclination_degrees" : 97.4540,
    #     "Perigee_Height_km" : 385,
    #     "Apogee_Height_km" : 392,
    #     "RAAN_degrees" : 267.4498,
    #     "Argument_of_Perigee_degrees" : 256.8657,
    #     "Mean_Anomaly_at_Epoch_degrees" : 103.1980,
    #     "Revolutions_per_Day" : 15.59560910,
    #     "Orbit_Number_at_Epoch" : 23_446,
    #     "Time_Eclipse_min" : 38.512,  # calculated by AI4CE software
    # }

    status, msg = _backend_POST(endpoint=f"/v2/projects/{project_id}/mission/", data=data)
    if status == 201:
        return msg
    else:
        print(f"Error setting mission/orbit info: {msg}")
        return {"error": msg}


def get_enabled_components(nested_dict, enabled_components=None) -> list:
    """
    Recursively traverses a nested dictionary to find and return a list of components that are enabled.

    Parameters:
    nested_dict (dict): The nested dictionary to traverse.
    enabled_components (list, optional): A list to store the names of the enabled components.
                                         Defaults to None, in which case a new list is created.

    Returns:
    list: A list of the names of the enabled components.
    """

    if enabled_components is None:
        enabled_components = []

    for key, value in nested_dict.items():
        if isinstance(value, dict):
            if value.get('Enabled') == True:
                enabled_components.append(key)
                pass
            get_enabled_components(value, enabled_components)

    return enabled_components


def traverse_and_modify(d: dict, sys_config_enabled: dict):
    for key, value in d.items():
        if isinstance(value, dict):
            component = key
            traverse_and_modify(d=value, sys_config_enabled=sys_config_enabled)
        else:
            # This block executes only if `value` is not a dict, i.e., at the deepest level
            # if d["Enabled"] is True or d["Enable"] is True or :
            try:
                if d["Enabled"] is True:
                    sys_config_enabled.update(enable_component(
                        component_name=key, data=load_file(Path("ai4ce/backend_sys_default.json"))))
            except KeyError as e:
                print("Error: ", e)


def enable_component(component_name: str, data: dict) -> dict:
    """Recursively search for a component in the nested dictionary from the backend
    and set 'enabled' to True if the feature name matches any key or value (case-insensitive).

    Parameters:
        data (dict): The nested dictionary to search within.
        feature_name (str): The feature name to search for, case-insensitively.

    Returns:
        dict: edited dict
    """

    for key, value in data.items():
        #  print(key, value)
        if isinstance(value, dict):
            enable_component(component_name, value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    enable_component(component_name, item)
        if key.lower() == component_name.lower() or str(value).lower() == component_name.lower():
            data['enabled'] = True
    return data


def set_sys_arch(project_id: int, sys_arch: dict) -> dict:
    """A function to set the system architecture in the project database.
    Params:
        project_id (int): The project Identification Number
        sys_arch(dict): Information about the satelllite's modules, which form the system architecture
    Returns:
        dict: html response from the backend to indicate success (200) or problems
     """

    sys_arch_example = {
        "system": {
            "eps": {
                "enabled": True,
                "battery": {
                    "enabled": True,
                }
            },
            "payload": {
                "camera": {
                    "enabled": True,
                }
            }
        }
    }

    response: dict = _backend_POST(
        endpoint=f"/v2/projects/{project_id}/system/", data=sys_arch)
    return response


def get_sys_arch(project_id: int) -> dict:
    """A function to get the system configuration info for a specific project based on its ID.
    Params:
        project_id (int): The project Identification Number

    Returns:
        dict: System information
    """

    response = _backend_GET(
        endpoint=f"/v2/projects/{project_id}/system/")
    return response

#  set_comp_list(project: int, not_yet_defined: dict)
# For each selected system generator, we need a place to store the corresponding found comp lists
# Every generator can produce n sets of components


def set_sys_generator(project_id: int, sys_gen_info: dict) -> dict:
    response = _backend_POST(
        endpoint=f"/v2/projects/{project_id}/sysgen/", data=sys_gen_info)
    return response


def update_sys_generator(project_id: int, sys_gen_info: dict) -> dict:
    response = _backend_PUT(
        endpoint=f"/v2/projects/{project_id}/sysgen/", data=sys_gen_info)
    return response


def set_trained_model(project_id: int, model_info: dict) -> dict:
    """A function to upload a trained AI model.
    Params:
        project_id (int): The project Identification Number
        model (ASKYOUNES): info about model

    Returns:
        dict: Upload server response
    """

    sta, msg = _backend_POST(endpoint=f"/v2/projects/{project_id}/sysgen/",
                             data=model_info)

    return msg


def get_prepared_system_generator_info(project_id: int) -> list:
    """A function to get all prepared system generators.
    Params:
        project_id (int): The project Identification Number

    Returns:
        list: list of dictionaries with infos for the prepared system generators
    """

    response = _backend_GET(
        endpoint=f"/v2/projects/{project_id}/sysgen/")
    return response


# def get_trained_model(project_id: int) -> mode: ASKYOUNES
#     pass


# def set_train_log(project_id: int, logs: ASKYOUNES) -> DB_response: ASKALEX
#     pass


# def get_train_logs(project_id: int) -> logs: ASKYOUNE   pass


def get_tags_from_string(str_of_tags: str) -> List[str]:
    """
    example_tags_str = "['satellite', 'power', 'solar-panels']"
    """
    # The string representation of a list of tags

    # Convert the string to an actual list using ast.literal_eval
    tags: list = ast.literal_eval(str_of_tags)
    return tags


def translate_tomlsystem_to_backend(system: dict, project_id: int) -> dict:
    """Translate a system configuration from a TOML file to a format that can be uploaded to the backend.

    Parameters:
    system (dict): The system configuration in TOML format.

    Returns:
    dict: The system configuration in a format that can be uploaded to the backend.
    """

    sys_config_enabled = {}
    # Loading System Configuration
    for key, value in system.items():
        if isinstance(value, dict):
            traverse_and_modify(d=value, sys_config_enabled=sys_config_enabled)

    resp = set_sys_arch(project_id=project_id, sys_arch=sys_config_enabled)
    pass
    return resp


def comp_create(comp_info: dict) -> dict:
    """Create a new component in the backend.
    Params:
        comp_info(dict): Information about the component
    Returns:
        dict:
    """
    status_code, msg = _backend_POST(
        endpoint=f"/v2/components/", data=comp_info)
    return status_code, msg

def get_all_decisions() -> dict:
    """Fetches all decisions from the DecisionDB and returns them as a dictionary.

    Returns:
        dict: A dictionary containing all decisions fetched from the DecisionDB.
    """
    response = _backend_GET(endpoint="/v2/components/export/")
    return response

def get_comp_statistics() -> dict:

    response =_backend_GET(endpoint="/v2/streamlit/db/stats/components")
    return response

