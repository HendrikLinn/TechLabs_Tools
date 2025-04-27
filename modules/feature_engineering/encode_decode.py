"""Contains function for encoding or decoding features."""

from typing import List

import pandas as pd
import numpy as np


def dummy_encode_column(
    data: pd.DataFrame, column: str, value: int = 1, egal_value: int = 3, inplace: bool = False
) -> pd.DataFrame:
    """Dummy encodes the input column in the ``data`` dataframe.
    Automatically decodes the value "Egal" to ``np.array([egal_value]``.
    The new names are like the original one with "_" and an upcounting number.

    Args:
        data (pd.DataFrame): Input dataframe.
        column (str): Column that should be dummy encoded.
        value (int, optional): Value which should be used for the dummy encoding. Defaults to 1.
        egal_value (int, optional): Value for the "Egal" value.
        inplace (bool, optional): If ``True``, the old column will be removed.. Defaults to False.

    Returns:
        pd.DataFrame: The original dataframe containing the dummy encoded column.
    """
    result = {}
    keys = data[column].unique()
    values = np.diag(np.full(len(keys), value))
    for i, key in enumerate(keys):
        result[key] = values[i]

    result["Egal"] = np.array(len(keys)*[egal_value])

    new_names = [column + "_" + str(num) for num in range(1, len(keys) + 1)]

    # Convert the series of arrays into a DataFrame with proper columns
    encoded_df = pd.DataFrame(data[column].map(result).tolist(), columns=new_names)

    if inplace:
        data.drop(column, inplace=inplace, axis=1)

    return pd.concat([data, encoded_df], axis=1)


def create_binary_encoding_time_slots(data: pd.DataFrame, days: List[str],time_columns: List[str], drop_old_cols: bool = True) -> pd.DataFrame:
    """Creates a binary encoding for all time slot columns in ``time_columns``. The list of ``days``
    represents the values present in the time columns, which are usually the days in a week.

    Args:
        data (pd.DataFrame): Dataframe in which the columns should be encoded.
        days (List[str]): Names of the days present in the time columns.
        time_columns (List[str]): Name of the time solumns.
        drop_old_cols (bool, optional): If True, the old columns are dropped in place.
        Defaults to True.

    Returns:
        pd.DataFrame: The original dataframe containing the new encoded columns.
    """

    # Create binary encoding for each time slot
    for time_col in time_columns:
        for day in days:
            data[f"{time_col}_{day}"] = data[time_col].apply(lambda x: 1 if day in x else 0)

    # Drop original columns if no longer needed
    return data.drop(columns=time_columns, inplace = drop_old_cols)
