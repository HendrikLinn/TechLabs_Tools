"""Thsi module contains utilities for all TechLabs tools."""
import json

def save_config(data: dict, filename: str) -> None:
    """Saves a configuration to a json file in the config directory.

    Args:
        data (dict): Data that should be saved in the given directory
    """
    with open("../config/" + filename, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_config(config_path: str) -> dict:
    """Loads the config from the given path.

    Args:
        config_path (str): Path to the config file.

    Returns:
        dict: Dictionary containing the configuration.
    """

    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")