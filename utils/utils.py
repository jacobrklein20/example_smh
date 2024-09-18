import pandas as pd


# Function for Scenario Dictionary
def scenario_info(scenario_file, round_number):
    """Create a dictionary with scenario id and full name

    Create a dictionary with scenario id and full name of a specific round

    :parameter scenario_file: Path to a csv file containing scenario information
    :type scenario_file: str
    :parameter round_number: Specific round number
    :type round_number: int
    :return scen_info: a dictionary with scenario id (key) and full name (value)
    """
    scen_info = pd.read_csv(scenario_file)
    scen_info = scen_info[scen_info["round"] == "round" + str(round_number)]
    scen_info = dict(zip(scen_info["scenario_id"], scen_info["scenario_fullname"]))
    return scen_info


def translate_col(df, col_name, col_dictionary, map_type=str):
    df[col_name] = df[col_name].map(map_type)
    df[col_name] = df[col_name].map(col_dictionary)
    return df


def calculate_rate(row, pop_value=100000):
    """Calculate population rate

    Calculate population rate by applying (row["value"] * pop_value / row["population"]) and
    round the output to 3 digits.

    :parameter row : Data Frame with a column "value" and a column "population"
    :type row: pandas.core.series.Series
    :parameter pop_value : list of round written as "round1" for example
    :type pop_value: int
    :return round_tab_list: population rate rounded by 3 digits
    """
    return round((row["value"] * pop_value / row["population"]), 3)


def calculate_zeroed_rate(row, pop_value=100000):
    """Calculate population rate with Zeroed file

    Calculate population rate by applying (row["value"] / row["population"]) * pop_value and
    round the output to 3 digits.

    :parameter row : Data Frame with a column "value" and a column "population"
    :type row: pandas.core.series.Series
    :parameter pop_value : list of round written as "round1" for example
    :type pop_value: int
    :return round_tab_list: population rate rounded by 3 digits
    """
    return round((row["value"] / row["population"]) * pop_value, 3)


def df_sort_location(loc_list):
    location_order = pd.DataFrame({
        'location_name': loc_list
    })
    sort_location = location_order.reset_index().set_index("location_name")
    return sort_location


def select_ts(df, df2, colname="target_end_date"):
    df_ts = list(df[colname].drop_duplicates())
    all_ts = list(set(list(df2[colname].drop_duplicates())).intersection(df_ts))
    all_ts.sort()
    return all_ts
