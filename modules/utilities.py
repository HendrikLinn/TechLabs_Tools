"""Thsi module contains utilities for all TechLabs tools."""
import json
from typing import Optional, Dict

from fuzzywuzzy import fuzz

def save_config(data: dict, filename: str) -> None:
    """Saves a configuration to a json file in the config directory.

    Args:
        data (dict): Data that should be saved in the given directory
    """
    with open("../config/" + filename, 'w', encoding = "utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_config(config_path: str) -> dict:
    """Loads the config from the given path.

    Args:
        config_path (str): Path to the config file.

    Returns:
        dict: Dictionary containing the configuration.
    """

    try:
        with open(config_path, 'r', encoding = "utf-8") as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def check_word_similarity(word1: str, word2: str, similarity: Optional[str] = "full") -> int:
    """Checks the similarity between two words based on the ``fuzzy.ratio`` or ``fuzzy.partial``
    depending on the provided similarity.

    Args:
        word1 (str): First word to compare.
        word2 (str): Second word to compare.
        similarity (Optional[str], optional): Similarity measure to use.
        Can be either "full" or "partial". Defaults to "full".

    Returns:
        int: The similarity between the two words.
    """
    if similarity == "partial":
        return fuzz.partial_ratio(word1, word2)
    else:
        return fuzz.ratio(word1, word2)

def get_key_from_list(dictionary: Dict[str, int], search_value: int) -> str:
    """Returns the matching key for the ``search_value`` the provided dictionary.

    Args:
        dictionary (Dict[str, int]): Dictionary to search in.
        search_value (int): Search value.

    Returns:
        str: Key of the searched value.
    """
    for key, val in dictionary.items():
        if val == search_value:
            return key
    return None
