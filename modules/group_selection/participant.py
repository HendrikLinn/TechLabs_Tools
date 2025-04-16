"""Contains all classes and functions for the participants."""

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

# Get the path to the higher-level directory
parent_dir = os.path.abspath(
    os.path.join(os.path.dirname("utilities.py"), "..", "modules")
)

# Add the directory to the Python path
sys.path.append(parent_dir)

import utilities


@dataclass
class Participant:
    """Class for participants."""

    id: int
    name: str
    group_id: int


def read_csv(file_path: str, delimiter: str = ",") -> List[Participant]:
    """Reads a csv file containing the participants.

    Args:
        file_path (str): Path to the csv file.
        delimiter (str, optional): Delimiter of the csv file. Defaults to ";".

    Returns:
        List[Participant]: List containing the participtans as objects of the
        ``Participants`` dataclass.
    """
    data = pd.read_csv(file_path, delimiter=delimiter)
    return [Participant(**row) for row in data.to_dict(orient="records")]


def read_excel(file_path: str) -> List[Participant]:
    """Reads an excel file containing the participants.

    Args:
        file_path (str): Path to the excel file.

    Returns:
        List[Participant]: List containin the participants as objects of the
        ``Participant`` dataclass.
    """
    data = pd.read_excel(file_path)
    return [Participant(**row) for row in data.to_dict(orient="records")]


def read_participants(file_path: str, delimiter: Optional[str]) -> List[Participant]:
    """Wrapper function for loading the file containing participants.

    Args:
        file_path (str): Path to the file.
        delimiter (Optional[str]): Optional delimiter if it is a csv file.

    Raises:
        ValueError: If the file type is neither csv or excel.

    Returns:
        List[Participant]: List containin the participants as objects of the
        ``Participant`` dataclass.
    """
    if file_path.endswith(".csv"):
        return read_csv(file_path, delimiter=delimiter)
    elif file_path.endswith(".xlsx"):
        return read_excel(file_path)
    else:
        raise ValueError("Unsupported file type")


def create_name_id_map(
    data: pd.DataFrame, name_columns: List[str], save_map: bool = True
) -> dict:
    """Creates a mapping of the participants names to ids.

    Args:
        data (pd.DataFrame): Dataframe containing the participant names.
        name_columns (List[str]): List of columns that contain the participant names.
        save_map (bool, optional): If True, the mapping is saved to a json file in
        the config directory. Defaults to True.

    Returns:
        dict: _description_
    """
    part_names = data[name_columns].agg("".join, axis=1)
    name_id_map = {}
    for name, name_id in zip(part_names, range(1, len(part_names) + 1)):
        name_id_map[name] = name_id

    if save_map:
        utilities.save_config(name_id_map, "name_id_map.json")

    return name_id_map


def get_index_of_most_similar_name_from_list(name: str, name_id_map: Dict[str, int]) -> int:
    """Returns the index of the most similar word in the input ``name_id_map``.

    Args:
        name (str): Name to check the similarity for.
        name_id_map (Dict): Dictionary containing the mapping between name and id.

    Returns:
        int: Returns the index of the most similar name.
    """
    similarities = [
        utilities.check_word_similarity(name, name_in_list)
        for name_in_list in name_id_map
    ]
    return similarities.index(max(similarities))


def get_most_similar_name_from_list(name: str, name_id_map: Dict[str, int]) -> str:
    """Returns the most similar word in the input ``name_id_map``

    Args:
        name (str): Name to check the similarity for.
        name_id_map (Dict): Dictionary containing the ampping between name and id.

    Returns:
        Dict[str: int]: The most similar name in the input ``name_id_map``
    """
    return list(name_id_map)[
        get_index_of_most_similar_name_from_list(name, list(name_id_map)) + 1
    ]
