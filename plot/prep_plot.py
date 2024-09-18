from datetime import datetime

import pandas as pd

from settings import viz_setting, invert_team_name, constant_dict
from utils.utils import translate_col


def prep_scenario_plot_df(df, df_gs_data, scenario, target, ens_check, round_tab):
    df.sort_values("scenario_id")
    df = df[df["scenario_id"].isin(map(int, scenario))]
    if (ens_check != ['True']) and (viz_setting[round_tab]["ensemble"]["hide"] is not None):
        team_rm = list()
        for i in viz_setting[round_tab]["ensemble"]["hide"]:
            team_rm.append(int(invert_team_name[i]))
        df = df[~df.model_name.isin(team_rm)]
    df = translate_col(df, "model_name", constant_dict["model_name"])
    if "constant" in viz_setting[round_tab]["scenario_plot"]:
        if target in viz_setting[round_tab]["scenario_plot"]["constant"].keys():
            if "value" in viz_setting[round_tab]["scenario_plot"]["constant"][target]:
                df["value"] = df["value"] + viz_setting[round_tab]["scenario_plot"]["constant"][target]["value"]
            elif "truth_date" in viz_setting[round_tab]["scenario_plot"]["constant"][target]:
                const_val = df_gs_data[df_gs_data["time_value"] ==
                                       viz_setting[round_tab]["scenario_plot"]["constant"][target]["truth_date"]]
                const_val = const_val[["value"]]
                df["value"] = df["value"] + const_val.iat[0, 0]
    return df


def prep_scenario_ui(ui, round_tab):
    if ui == -1:
        intervals = None
        point_value = None
    else:
        intervals = ui / 100
        if intervals == 0:
            intervals = []
        if viz_setting[round_tab]["point"]["type"] == "point":
            point_value = "point"
        elif (viz_setting[round_tab]["point"]["type"] == "quantile" and
              viz_setting[round_tab]["point"]["type_id"] == 0.5):
            point_value = "median"
        else:
            point_value = None
    return intervals, point_value


def prep_scenario_zoom(df, df_gs_data, target, round_tab):
    if df_gs_data is not None and target == "inc hosp":
        s_week = pd.offsets.DateOffset(months=3)
    else:
        s_week = pd.offsets.DateOffset(weeks=1)
    max_gs = 0
    if df is not None:
        end_date = max(df[df["model_name"] == viz_setting[round_tab]["ensemble"]["default"]]["target_end_date"])
        start_date = datetime.strptime(min(df["target_end_date"]), "%Y-%m-%d") - s_week
        start_date = start_date.strftime("%Y-%m-%d")
        if df_gs_data is not None:
            if len(df_gs_data) > 0:
                if target == "cum death":
                    max_gs = max(df_gs_data[df_gs_data["time_value"] > start_date]["max"])
                else:
                    max_gs = max(df_gs_data[df_gs_data["time_value"] > start_date]["value"])
        y_max = max([max_gs, max(df[df["type_id"].isin([0.5, float("NaN")])]["value"])]) * 1.2
    else:
        if df_gs_data is not None:
            if len(df_gs_data) > 0:
                start_date = min(df_gs_data["time_value"])
                end_date = max(df_gs_data["time_value"])
                if target == "cum death":
                    y_max = max(df_gs_data[df_gs_data["time_value"] > start_date]["max"])
                else:
                    y_max = max(df_gs_data[df_gs_data["time_value"] > start_date]["value"])
            else:
                start_date = end_date = viz_setting[round_tab]["date_round"]
                y_max = 10
        else:
            start_date = end_date = viz_setting[round_tab]["date_round"]
            y_max = 10
    zoom_dict = {"x_min": start_date, "x_max": end_date, "y_min": -10, "y_max": y_max}
    return zoom_dict


def prep_scenario_v_lines(df, round_tab, zoom_dict):
    if df is not None:
        proj_date = datetime.strptime(min(df["target_end_date"]), "%Y-%m-%d") - pd.offsets.DateOffset(weeks=1)
    else:
        proj_date = (datetime.strptime(viz_setting[round_tab]["date_round"], "%Y-%m-%d") -
                     pd.offsets.DateOffset(days=1))
    proj_date = proj_date.strftime("%Y-%m-%d")
    today_date = datetime.today()
    today_date = today_date.strftime("%Y-%m-%d")
    if today_date < zoom_dict["x_max"]:
        v_lines = {"projection": {"x": proj_date, "line_width": 2, "line_color": "gray", "line_dash": "solid"},
                   "current_week": {"x": today_date, "line_width": 1, "line_color": "gray", "line_dash": "dash"}}
    else:
        v_lines = {"projection": {"x": proj_date, "line_width": 2, "line_color": "gray", "line_dash": "solid"}}
    return v_lines


def prep_scenario_h_lines(location, target, round_tab, df=None):
    if viz_setting[round_tab]["scenario_plot"]["peak"] is not None:
        list_hdict = list()
        h_lines = {}
        for key in viz_setting[round_tab]["scenario_plot"]["peak"].keys():
            if target == viz_setting[round_tab]["scenario_plot"]["peak"][key]["target_specific"]:
                if df is None:
                    df_threshold = viz_setting[round_tab]["scenario_plot"]["peak"][key]["file_name"]
                    df_threshold = pd.read_csv(df_threshold + ".csv")
                    df_threshold = df_threshold[df_threshold["region"] == location]
                    df_threshold = df_threshold[[viz_setting[round_tab]["scenario_plot"]["peak"][key]["col_name"]]]
                    h_dict = {"value": df_threshold.iat[0, 0], "text": "<b>" + key + "</b>: " +
                                                                       str(int(df_threshold.iat[0, 0])),
                              "color": "red", "font_color": "darkred", "font_size": 12}
                else:
                    df_threshold = df[df["time_value"] >=
                                      viz_setting[round_tab]["scenario_plot"]["peak"][key]["start_date"]]
                    df_threshold = df_threshold[df_threshold["time_value"] <=
                                                viz_setting[round_tab]["scenario_plot"]["peak"][key]["end_date"]]
                    h_dict = {"value": max(df_threshold["value"]),
                              "text": "<b>" + key + "</b>: " + str(int(max(df_threshold["value"]))),
                              "color": "red", "font_color": "darkred", "font_size": 12}
                list_hdict.append(h_dict)
        for index, element in enumerate(list_hdict):
            h_lines[index] = element
    else:
        h_lines = None
    return h_lines
