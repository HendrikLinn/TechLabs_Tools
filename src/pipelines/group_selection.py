"""The main pipeline for processing the participants data."""

from typing import Dict
import sys
import os

import numpy as np
import pandas as pd

# Get the path to the higher-level directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname("participant.py"), ".."))

# Add the directory to the Python path
sys.path.append(parent_dir)

# Import participant module
from modules.group_selection.participant import (
    create_name_id_map,
    get_index_of_most_similar_name_from_list,
)
from modules.feature_engineering.encode_decode import (
    dummy_encode_column,
    create_binary_encoding_time_slots,
)

######################
### Pre-processing ###
######################


def preprocessing_pipeline(
    participant_answers: pd.DataFrame, column_mapping: Dict, data_columns: Dict
) -> pd.DataFrame:
    """Perform preprocessing pipeline on raw participant answers.

    Processes and cleans the input dataFrame by removing unnecessary columns,
    renaming columns, handling missing data for personal preferences and time slots.
    Returns a cleaned dataFrame with processed data.

    Args:
        participant_answers (pd.DataFrame): Participant answers.
        column_mapping (Dict): Mapping of original column names to more readable ones.
        data_columns (Dict): Contains data ranges for columns, e. g. names of weekdays.

    Returns:
        pd.DataFrame: Preprocessed participant data.
    """
    # Load raw participants data
    participants_raw = pd.read_csv(participant_answers, delimiter=",")

    # Removed unnecessary columns which are exported by typeform
    participants_data = participants_raw.drop(
        [
            "#",
            "Response Type",
            "Start Date (UTC)",
            "Stage Date (UTC)",
            "Submit Date (UTC)",
            "Network ID",
            "Tags",
            "feedback",
        ],
        axis=1,
    )

    # Rename column
    participants_data.rename(column_mapping, axis=1, inplace=True)

    # Handle missing data in personal_preferences and time slots.
    participants_data.fillna({"personal_preferences": ""}, inplace=True)

    # Handling missing data in personal_preferences and time slots.
    participants_data.fillna({"personal_preferences": ""}, inplace=True)
    participants_data[data_columns["time_columns"]] = participants_data[
        data_columns["time_columns"]
    ].fillna("no availability")

    return participants_data


###########################
### Feature Engineering ###
###########################


def feature_engineering_pipeline(
    participants_data: pd.DataFrame,
    data_columns: Dict,
    first_name_column: str,
    surname_column: str,
) -> pd.DataFrame:
    """Feature engineering pipeline for the group selection process.

    Args:
        participants_data (pd.DataFrame): Contains the participant data.
        data_columns (Dict): Inormation on data ranges for columns where necessary.
        first_name_column (str): Column name containing the first name.
        surname_column (str): Column name containing the surname.

    Returns:
        pd.DataFrame: Dataframe containing the generated features.
    """

    # Create binary encoding for the time slot columns
    participants_data = create_binary_encoding_time_slots(
        participants_data,
        days=data_columns["week_days"],
        time_columns=data_columns["time_columns"],
        drop_old_cols=True,
    )

    # Dummy encode the priority topic columns
    participants_data = dummy_encode_column(
        participants_data, "priority_topic1", 3, inplace=True
    )
    participants_data = dummy_encode_column(
        participants_data, "priority_topic2", 2, inplace=True
    )
    participants_data = dummy_encode_column(
        participants_data, "priority_topic3", 1, inplace=True
    )

    # Create a name id map for the individual names in the participant dataframe
    name_id_map = create_name_id_map(
        participants_data, [first_name_column, surname_column]
    )

    # Add the id from the name_id_map in the column id
    participants_data["id"] = (
        participants_data[[first_name_column, surname_column]]
        .agg("".join, axis=1)
        .apply(lambda x: name_id_map[x])
    )

    # Remove columns containing the names
    participants_data.drop([first_name_column, first_name_column], axis=1, inplace=True)

    # Encode the english preference to 0 and 1
    participants_data["english"] = participants_data["english"].map(
        {"Nein": 0, "Egal": 1, "Ja": 1}
    )

    # Encode the experience from 1 to 3
    participants_data["experience"] = participants_data["experience"].map(
        {"Keine Vorkenntnisse": 1, "Basiswissen": 2, "Gute Vorkenntnisse": 3}
    )

    # Encodee the preference group to either 0 in case of no preference and
    # to 1 in case of psychology group
    participants_data["preference_group"] = participants_data["preference_group"].map(
        {
            np.nan: 0,
            "Keine Präferenz": 0,
            "Eine Gruppe nur mit Psychologie Studierenden": 1,
        }
    )

    # Combine the personal preferences into keys (names without spaces) for easier handling
    participants_data["personal_preferences_keys"] = participants_data[
        "personal_preferences"
    ].apply(lambda x: [name.replace(" ", "") for name in x.split(", ")])

    # Get ids of the participants_data named in personal_preferences_keys and combine the ids in a list
    participants_data["personal_preferences_ids"] = participants_data[
        "personal_preferences_keys"
    ].apply(
        lambda x: [
            (
                get_index_of_most_similar_name_from_list(name, name_id_map.keys()) + 1
                if name != ""
                else np.nan
            )
            for name in x
        ]
    )

    # Remove processed columns
    participants_data.drop(
        ["personal_preferences_keys", "personal_preferences"], axis=1, inplace=True
    )

    return participants_data
