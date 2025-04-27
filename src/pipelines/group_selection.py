"""The main pipeline for processing the participants data."""

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
from modules import utilities
from modules.feature_engineering.encode_decode import (
    dummy_encode_column,
    create_binary_encoding_time_slots,
)

# Load column mapping for column names
column_mapping = utilities.load_config("../config/column_mapping.json")

# set days of the week of the week
week_days = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]
time_columns = ["time1", "time2", "time3", "time4", "time5", "time6", "time7"]
first_name_column = "name"
surname_column = "surname"


######################
### Pre-processing ###
######################

# Load raw participants data
participants_raw = pd.read_csv("../data/responses.csv", delimiter=",")

# Removed unnecessary columns which are exported by typeform
participants = participants_raw.drop(
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
participants.rename(column_mapping, axis=1, inplace=True)

# Handling missing data in personal_preferences and time slots.
participants.fillna({"personal_preferences": ""}, inplace=True)
participants[["time1", "time2", "time3", "time4", "time5", "time6", "time7"]] = (
    participants[
        ["time1", "time2", "time3", "time4", "time5", "time6", "time7"]
    ].fillna("no availability")
)

###########################
### Feature Engineering ###
###########################

# Create binary encoding for the time slot columns
participants = create_binary_encoding_time_slots(
    participants, days=week_days, time_columns=time_columns, drop_old_cols=True
)

# Dummy encode the priority topic columns
participants = dummy_encode_column(participants, "priority_topic1", 3, inplace=True)
participants = dummy_encode_column(participants, "priority_topic2", 2, inplace=True)
participants = dummy_encode_column(participants, "priority_topic3", 1, inplace=True)

# Create a name id map for the individual names in the participant dataframe
name_id_map = create_name_id_map(participants, [first_name_column, surname_column])

# Add the id from the name_id_map in the column id
participants["id"] = (
    participants[[first_name_column, surname_column]]
    .agg("".join, axis=1)
    .apply(lambda x: name_id_map[x])
)

# Remove columns containing the names
participants.drop([first_name_column, first_name_column], axis=1, inplace=True)

# Encode the english preference to 0 and 1
participants["english"] = participants["english"].map({"Nein": 0, "Egal": 1, "Ja": 1})

# Encode the experience from 1 to 3
participants["experience"] = participants["experience"].map(
    {"Keine Vorkenntnisse": 1, "Basiswissen": 2, "Gute Vorkenntnisse": 3}
)

# Encodee the preference group to either 0 in case of no preference and
# to 1 in case of psychology group
participants["preference_group"] = participants["preference_group"].map(
    {np.nan: 0, "Keine Präferenz": 0, "Eine Gruppe nur mit Psychologie Studierenden": 1}
)

# Combine the personal preferences into keys (names without spaces) for easier handling
participants["personal_preferences_keys"] = participants["personal_preferences"].apply(
    lambda x: [name.replace(" ", "") for name in x.split(", ")]
)

# Get ids of the participants named in personal_preferences_keys and combine the ids in a list
participants["personal_preferences_ids"] = participants[
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
participants.drop(
    ["personal_preferences_keys", "personal_preferences"], axis=1, inplace=True
)
