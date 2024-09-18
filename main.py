import random
import time

import dash
import polars as pl
from dash import Dash, Output, Input
from flask_caching import Cache

from SMHviz_layout.metadata_content import *
from SMHviz_layout.notes_definition import *
from SMHviz_layout.tabs import make_tab_plots
from SMHviz_layout.plottab_bar import make_plot_bar
from SMHviz_layout.sidebar import make_sidebar
from SMHviz_plot.figures import *
from SMHviz_plot.utils_data import *

from plot.prep_plot import *
from settings import *
from utils.utils import *

# App ---
app = Dash(__name__,
           external_stylesheets=["./assets/style.css"],
           suppress_callback_exceptions=True,
           use_pages=True)

server = app.server

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = None

app.layout = html.Div([
    html.Div(
        [
            html.Div([
                dcc.Link("Scenario Definition", href=dash.page_registry["pages.scenario_definition"]["path"],
                         className="menu_pages"),
                dcc.Link("Model Metadata", href=dash.page_registry["pages.model_metadata"]["path"],
                         className="menu_pages"),
                dcc.Link("Plots", href=dash.page_registry["pages.plots"]["path"], className="menu_pages"),
            ]),
            html.Br()
        ]
    ),
    html.Br(),
    dash.page_container
])


@cache.memoize(timeout=TIMEOUT)
def query_proj_data(location, target, type_name, round_number, path="./visualization/data-visualization/models/",
                    filename="part-0"):
    if location is None:
        file_name = path + "round" + str(round_number) + "/" + target + "/" + type_name + "/" + filename
    else:
        file_name = (path + "round" + str(round_number) + "/" + target + "/" + location + "/" + type_name + "/" +
                     filename)
    if type_name == "sample":
        file_name = file_name + ".parquet"
    else:
        file_name = file_name + ".csv"
    if os.path.isfile(file_name):
        if type_name == "sample":
            df = pl.scan_parquet(file_name)
            df = df.collect()
            df = df.to_pandas()
        else:
            df = pd.read_csv(file_name)
        order_col = []
        if "scenario_id" in df.columns:
            order_col.append("scenario_id")
        if "target_end_date" in df.columns:
            order_col.append("target_end_date")
        if len(order_col) > 0:
            df = df.sort_values(order_col)
    else:
        print("File not found: " + file_name)
        df = None
    return df


@cache.memoize(timeout=TIMEOUT)
def query_gs_data(filename, location, age_group, path="./visualization/data-goldstandard/"):
    file_name = path + filename + ".csv"
    if os.path.isfile(file_name):
        df = pd.read_csv(file_name)
        # filter target
        if "target" in df.columns:
            df = df[~df["target"].str.contains("rate")]
        # filter location
        if location is not None:
            if "geo_value_fullname" in df.columns:
                df = df[df["geo_value_fullname"] == location]
            else:
                df = df.merge(location_info[["location", "location_name"]])
                df = df[df["location_name"] == location]
                df = df.rename(columns={"date": "time_value"})
        if age_group is not None:
            df = df[df["age_group"] == age_group]
        # remove negative value
        df.loc[df["value"] < 0, "value"] = float("NaN")
        df = df.sort_values("time_value")
    else:
        print("File not found: " + file_name)
        df = None
    return df


@cache.memoize(timeout=TIMEOUT)
def prep_model_data(sel_target, location, model, quant_sel, age_group, round_number, invert_team):
    df_all = []
    for i in sel_target:
        df = query_proj_data(location, i, "quantile", round_number)
        if df is not None:
            df = df[df["age_group"] == age_group]
            df = df[df["type_id"].isin(quant_sel)]
            df["target"] = i
            df = df.sort_values(by=["scenario_id", "target", "target_end_date"])
        else:
            df = pd.DataFrame()
        df_all.append(df)
    df_all = pd.concat(df_all)
    if model is not None and len(df_all) > 0:
        df_all = df_all[df_all["model_name"] == int(invert_team[model])]
    return df_all


@cache.memoize(timeout=TIMEOUT)
def prep_gs_data(sel_target, location, age_group, viz_set, round_tab):
    df_gs_all = []
    for i in sel_target:
        df_gs_data = viz_set[round_tab]["gold_standard"][i]
        if df_gs_data is not None:
            df_gs_data = query_gs_data(df_gs_data, location, age_group)
            df_gs_data["target"] = i
            df_gs_all.append(df_gs_data)
    if len(df_gs_all) > 0:
        df_gs_all = pd.concat(df_gs_all)
    else:
        df_gs_all = None
    return df_gs_all


@cache.memoize(timeout=TIMEOUT)
def scenario_plot_prep(scenario, location, target, ui, age_group, ens_check, round_tab):
    # Prerequisite
    round_number = viz_setting[round_tab]["round_number"]
    target_dict = viz_setting[round_tab]["target"]
    df_gs_data = viz_setting[round_tab]["gold_standard"][target]
    color_dict = constant_dict["color_dict"]
    # Data
    truth_data_type = "scatter"
    if df_gs_data is not None:
        df_gs_data = query_gs_data(df_gs_data, location, age_group)
        if df_gs_data is not None:
            if len(df_gs_data) == 0:
                df_gs_data = None
    df = query_proj_data(location, target, "quantile", round_number)
    df = df[df["age_group"] == age_group]
    if df is not None:
        df = prep_scenario_plot_df(df, df_gs_data, scenario, target, ens_check, round_tab)
    # Plot information
    scen_info = scenario_info(scen_file, round_number)
    intervals, point_value = prep_scenario_ui(ui, round_tab)
    y_title = target_dict[target]
    truth_legend = y_title
    sub_scen = list()
    if (df is None) or (len(df) == 0):
        title = None
        sub_scen.append(title)
    else:
        for scen in df["scenario_id"].unique():
            title = ("<br>Scenario " + re.findall("^\\D", constant_dict["scenario_id"][str(scen)])[0] + ": " +
                     re.sub(", | and ", ",<br>", scen_info[constant_dict["scenario_id"][str(scen)]]))
            sub_scen.append(title)
    title = ("<b>Projected " + y_title.title() + " by Epidemiological Week and by Scenario for " + round_tab + " (" +
             age_group + ")")
    # zoom
    zoom_dict = prep_scenario_zoom(df, df_gs_data, target, round_tab)
    # Vertical line
    v_lines = prep_scenario_v_lines(df, round_tab, zoom_dict)
    # Horizontal line
    h_lines = prep_scenario_h_lines(location, target, round_tab, df=df_gs_data)
    prep_scenario = {"df": df, "df_gs_data": df_gs_data, "intervals": intervals, "x_title": "Epiweek",
                     "y_title": y_title, "hover_text": "Model Name: %{model_name}<br>",
                     "ensemble_name": viz_setting[round_tab]["ensemble"]["default"], "h_lines": h_lines,
                     "ensemble_color": "rgba(0, 0, 0, 1)", "ensemble_view": True, "color_dict": color_dict,
                     "title": title, "subplot_title": sub_scen, "point_value": point_value,
                     "truth_data_type": truth_data_type, "zoom_in_projection": zoom_dict, "v_lines": v_lines,
                     "truth_legend_name": truth_legend}
    return prep_scenario


@cache.memoize(timeout=TIMEOUT)
def spaghetti_plot_prep(scenario, location, target, age_group, n_sample, med_plot, round_tab):
    round_number = viz_setting[round_tab]["round_number"]
    target_dict = viz_setting[round_tab]["target"]
    color_dict = constant_dict["color_dict"]
    df = query_proj_data(location, target, "sample", round_number)
    df = df[df["age_group"] == age_group]
    scenario.sort()
    if n_sample < 20:
        opacity = 0.3
    elif n_sample < 40:
        opacity = 0.2
    else:
        opacity = 0.1
    if (df is None) or (len(df) == 0):
        prep_plot = {"df": None, "subplot_titles": None, "title": "", "opacity": opacity, "color_dict": color_dict,
                     "y_title": target_dict[target]}
        return prep_plot
    df = df[df["scenario_id"].isin(map(int, scenario))]
    if len(df) > 0:
        scen_info = scenario_info(scen_file, round_number)
        sub_scen = list()
        df["type_id"] = df["type_id"].map(int)
        df = df[["scenario_id", "value", "type_id", "model_name", "target_end_date"]]
        df_sel = list()
        for scen in df["scenario_id"].unique():
            title = ("Scenario " + re.findall("^\\D", constant_dict["scenario_id"][str(scen)])[0] + ": " +
                     re.sub(", | and ", ",<br>", scen_info[constant_dict["scenario_id"][str(scen)]]))
            sub_scen.append(title)
            df_scen = df[df["scenario_id"] == scen]
            for model in df_scen["model_name"].drop_duplicates():
                df_mod = df_scen[df_scen["model_name"] == model]
                type_id_sel = random.sample(list(df_mod["type_id"].drop_duplicates()), n_sample)
                df_mod = df_mod[df_mod["type_id"].isin(type_id_sel)]
                df_sel.append(df_mod)
        df = pd.concat(df_sel)
        title = "Projected " + target_dict[target] + " by Epidemiological Week and by Scenario for " + round_tab
        if med_plot is not None and med_plot == [True]:
            df_med = query_proj_data(location, target, "quantile", round_number)
            df_med = df_med[df_med["type_id"] == 0.5]
            df_med = df_med[df_med["age_group"] == age_group]
            df_med = df_med[df_med["model_name"].isin(df["model_name"].drop_duplicates())]
            df_med = df_med[["scenario_id", "value", "type_id", "model_name", "target_end_date"]]
            df = pd.concat([df, df_med])
        df["model_name"] = df["model_name"].map(str)
        df = df.sort_values(["scenario_id", "target_end_date"])
        prep_plot = {"df": df, "subplot_titles": sub_scen, "title": title, "opacity": opacity, "color_dict": color_dict,
                     "y_title": target_dict[target]}
    else:
        prep_plot = {"df": None, "subplot_titles": None, "title": "", "opacity": opacity, "color_dict": color_dict,
                     "y_title": target_dict[target]}
    return prep_plot


@cache.memoize(timeout=TIMEOUT)
def specific_plot_prep(model, location, target_type, ui, age_group, round_tab):
    # Prerequisite
    round_number = viz_setting[round_tab]["round_number"]
    target_list = viz_setting[round_tab]["target"]
    scen_info = scenario_info(scen_file, round_number)
    sel_target = [x for x in list(target_list.keys()) if re.findall(target_type, x)]
    subplot_title = list()
    for targ in sel_target:
        subplot_title.append(target_list[targ])
    quant_sel = ui_dict[ui].copy()
    if viz_setting[round_tab]["point"]["type"] == "point":
        quant_sel[quant_sel.index(0.5)] = float("NaN")
    else:
        quant_sel = ui_dict[ui]
    title = "Model Specific Projections, by Scenario - " + round_tab + " - " + str(location)
    # Data
    df_all = prep_model_data(sel_target, location, model, quant_sel, age_group, round_number, invert_team_name)
    df_gs_all = prep_gs_data(sel_target, location, age_group, viz_setting, round_tab)
    if df_all is None or len(df_all) == 0:
        prep_plot = {
            "df": None, "df_gs_data": df_gs_all, "intervals": 0, "point_value": None,
            "subplot_title": sel_target, "title": title, "legend_dict": scen_info
        }
        return prep_plot
    if df_gs_all is not None and df_all is not None:
        df_gs_all = df_gs_all[df_gs_all["time_value"] <= max(df_all["target_end_date"])]
        start_date = (datetime.strptime(min(df_all["target_end_date"]), "%Y-%m-%d") -
                      pd.offsets.DateOffset(months=4))
        start_date = start_date.strftime("%Y-%m-%d")
        df_gs_all = df_gs_all[df_gs_all["time_value"] >= start_date]
    if "cum hosp" in sel_target and df_gs_all is not None:
        df_gs_all = df_gs_all[df_gs_all["target"] == "cum hosp"]
    # Plot preparation
    df_all["scenario_id"] = df_all["scenario_id"].map(str)
    df_all["scenario_id"] = df_all["scenario_id"].map(constant_dict["scenario_id"])
    intervals, point_value = prep_scenario_ui(ui, round_tab)
    # Return all information
    prep_plot = {
        "df": df_all, "df_gs_data": df_gs_all, "intervals": intervals, "point_value": point_value,
        "subplot_title": subplot_title, "title": title, "legend_dict": scen_info
    }
    return prep_plot


@cache.memoize(timeout=TIMEOUT)
def comparison_plot_prep(location, age_group, multi_ref, round_tab):
    # Prerequisite
    round_number = viz_setting[round_tab]["round_number"]
    target_list = viz_setting[round_tab]["target"]
    ens_name = viz_setting[round_tab]["ensemble"]["default"]
    quant_sel = ui_dict[0].copy()
    if "multi_panel" in viz_setting[round_tab]["scenario_comparison"]:
        comparison_reference = viz_setting[round_tab]["scenario_comparison"]["multi_panel"][multi_ref]
        comparison_reference = comparison_reference["reference"]
    else:
        comparison_reference = viz_setting[round_tab]["scenario_comparison"]["reference"]

    if viz_setting[round_tab]["point"]["type"] == "point":
        quant_sel[quant_sel.index(0.5)] = float("NaN")
    else:
        quant_sel = ui_dict[0]
    zeroed = viz_setting[round_tab]["zeroed_file"]
    if zeroed == "Sample":
        sel_target = [x for x in list(target_list.keys()) if re.findall("cum", x)]
        method = end_cum_value
    else:
        sel_target = [x for x in list(target_list.keys()) if re.findall("inc", x)]
        method = model_cum_data
    # Data
    df = prep_model_data(sel_target, location, None, quant_sel, age_group, round_number,
                         None)
    if len(df) == 0:
        prep_plot = {
            "df": None, "ens_name": ens_name, "comparison": comparison_reference, "title": None,
            "subplot_title": None, "color_dictionary": constant_dict["color_dict"]
        }
    else:
        max_ens_week = max(df[df["model_name"] == int(invert_team_name[ens_name])]["horizon"])
        df["scenario_id"] = df["scenario_id"].map(str)
        df["scenario_id"] = df["scenario_id"].map(constant_dict["scenario_id"])
        df["model_name"] = df["model_name"].map(str)
        df["model_name"] = df["model_name"].map(constant_dict["model_name"])
        df["target"] = df["target"].map(target_list)
        df = scen_comparison_data(df, max_week=max_ens_week, end_method=method,
                                  comparison_reference=comparison_reference,
                                  model_exclusion=viz_setting[round_tab]["ensemble"]["hide"])
        title = ("Excess Percentage of reported hospitalizations compared with the counterfactual scenario (" +
                 location + "); Projection Wk 1-" + str(max_ens_week))
        df = df.sort_values(["scen_comp", "model_name"])
        subplot_title = list(df["comparison"].unique())
        # Plot
        prep_plot = {
            "df": df, "ens_name": ens_name, "comparison": comparison_reference, "title": title,
            "subplot_title": subplot_title}
    return prep_plot


@cache.memoize(timeout=TIMEOUT)
def peak_time_prep(scenario, model, order, round_tab):
    # prerequisite
    round_number = viz_setting[round_tab]["round_number"]
    loc_list = pd.DataFrame()
    if order == "Geographical":
        loc_list = pd.concat([loc_list, (df_sort_location(["US"] + constant_dict["location_order"]))])
    elif order == "Alphabetical":
        state_list = constant_dict["location_order"].copy()
        state_list.sort(reverse=True)
        loc_list = pd.concat([loc_list, df_sort_location(["US"] + state_list)])
    else:
        loc_list = pd.concat([loc_list, (df_sort_location(["US"] + constant_dict["location_order"]))])
    scenario = list(map(int, scenario))
    scenario.sort()
    # data
    df = query_proj_data(None, "peak time hosp", "pdf", round_number)
    df = df[df["scenario_id"].isin(map(int, scenario))]
    df = translate_col(df, "model_name", constant_dict["model_name"])
    df = df[df["model_name"] == model]
    df = df[df["location_name"].isin(["US"] + constant_dict["location_order"])]
    df["order"] = df["location_name"].map(loc_list["index"])
    df = df.sort_values(["scenario_id", "horizon", "order"])
    # plot parameter
    subplot_title = list()
    for scen in scenario:
        subplot_title.append(constant_dict["scenario_id"][str(scen)])
    prep_plot = {"df": df, "subplot_title": subplot_title}
    return prep_plot


@cache.memoize(timeout=TIMEOUT)
def peak_size_prep(scenario, location, round_tab):
    # prerequisite
    round_number = viz_setting[round_tab]["round_number"]
    ens_name = [viz_setting[round_tab]["ensemble"]["default"]]
    if viz_setting[round_tab]["ensemble"]["hide"] is not None:
        for ens in viz_setting[round_tab]["ensemble"]["hide"]:
            ens_name.append(ens)
    subplot_title = list()
    scenario = list(map(int, scenario))
    scenario.sort()
    scen_info = scenario_info(scen_file, round_number)
    for scen in scenario:
        subplot_title.append(constant_dict["scenario_id"][str(scen)] + ": " +
                             re.sub(", | and ", ",<br>",
                                    scen_info[constant_dict["scenario_id"][str(scen)]]))
    # data
    df = query_proj_data(location, "peak size hosp", "quantile", round_number)
    if df is not None:
        df = df[df["scenario_id"].isin(map(int, scenario))]
        df = translate_col(df, "model_name", constant_dict["model_name"])
        df = df.sort_values(["scenario_id"])
        df_proj = df.copy()
        df_proj = df_proj[~df_proj["model_name"].isin(ens_name)]
        df_proj = df_proj.sort_values(["model_name"], ascending=False)
        df_ens = df.copy()
        df_ens = df_ens[df_ens["model_name"] == viz_setting[round_tab]["ensemble"]["default"]]
        # plot parameter
        model_color_dict = dict()
        for val in df_proj["model_name"].unique():
            model_color_dict.update({val: "black"})
        for val in df_ens["model_name"].unique():
            model_color_dict.update({val: "darkgreen"})
        df_plot = pd.concat([df_ens, df_proj])
    else:
        df_plot = model_color_dict = None
    prep_plot = {"df": df_plot, "subplot_title": subplot_title, "color_dict": model_color_dict}
    return prep_plot


@cache.memoize(timeout=TIMEOUT)
def prep_pathogen_data(df, scenario, pathogen, k=1000):
    if df is not None:
        df_sample = sample_df(df, scenario, pathogen, k=k)
    else:
        df_sample = pd.DataFrame()
    return df_sample


@cache.memoize(timeout=TIMEOUT)
def multi_pathogen_obs_prep(round_tab, target, location, patho_selected, time_series):
    # Prerequisite
    pathogen_name = constant_dict["pathogen_display_name"]
    # Flu Truth Data
    df_gs_data = viz_setting[round_tab]["gold_standard"][target]
    if df_gs_data is not None:
        df_gs_data = query_gs_data(df_gs_data, location, age_group="0-130")
    # Other Pathogen Truth Data
    other_df_gs = pd.DataFrame()
    for patho in patho_selected:
        df_gs_other_data = query_gs_data(target, location, age_group=None,
                                         path="./visualization/data-goldstandard/" + patho.lower() + "/")
        if df_gs_other_data is not None:
            if "target" in df_gs_other_data.columns:
                df_gs_other_data = df_gs_other_data[df_gs_other_data["target"] == target]
                df_gs_other_data = df_gs_other_data[["time_value", "geo_value_fullname", "fips", "value"]]
            df_gs_other_data = df_gs_other_data.rename(columns={"value": "value_" + patho.lower()})
            if len(other_df_gs) < 1:
                other_df_gs = df_gs_other_data
            else:
                other_df_gs = pd.merge(other_df_gs, df_gs_other_data)
    # Calculate sum of the time series
    if df_gs_data is not None:
        if len(other_df_gs) >= 1:
            total_gs = pd.merge(other_df_gs, df_gs_data)
            total_gs["total_value"] = total_gs[[col for col in total_gs.columns if
                                                col.startswith('valu')]].sum(axis=1, skipna=False)
            total_gs = total_gs[["time_value", "total_value"]]
            df_gs_data = pd.merge(df_gs_data, total_gs)
        else:
            df_gs_data["total_value"] = np.nan
        df_gs_data = df_gs_data.sort_values(["time_value"])
        if "peak" in viz_setting[round_tab]["multi-pathogen_plot"]:
            peaks = list()
            for peak_name in viz_setting[round_tab]["multi-pathogen_plot"]["peak"]:
                peak_date = viz_setting[round_tab]["multi-pathogen_plot"]["peak"][peak_name]
                flu_peak = df_gs_data[df_gs_data["time_value"] > peak_date["start_date"]]
                flu_peak = flu_peak[flu_peak["time_value"] < peak_date["end_date"]]
                flu_peak = flu_peak[["time_value", "value", "total_value"]]
                flu_peak_value = max(flu_peak["value"])
                tot_peak_value = np.amax(flu_peak["total_value"])
                peaks.append({"name": pathogen_name + " " + peak_name, "value": flu_peak_value})
                peaks.append({"name": " + ".join(patho_selected + [pathogen_name]) + " " + peak_name,
                              "value": tot_peak_value})
        else:
            peaks = [None]
        df_gs_data = df_gs_data[df_gs_data["time_value"].isin(time_series)]
    else:
        peaks = [None]
    return {"df_gs_data": df_gs_data, "peaks": peaks}


@cache.memoize(timeout=TIMEOUT)
def multi_pathogen_combined_prep(location, target, scenario, other_scen, round_tab, k=10000):
    # Prerequisite
    round_number = viz_setting[round_tab]["round_number"]
    pathogen = constant_dict["pathogen"].lower()
    pathogen_disp_name = constant_dict["pathogen_display_name"]
    pathogen_set = viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"]
    other_pathogen = list(other_scen.keys())
    other_pathogen_data = {}
    for patho in other_pathogen:
        rnd_n = pathogen_set[patho]["round"]
        other_pathogen_data.update({patho: {"round_number": re.findall("\d+", rnd_n)[0]}})
    # Data
    df = query_proj_data(location, target, "sample", round_number)
    df = df[df["age_group"] == "0-130"]
    if df is not None and len(df) > 0:
        flu_ts = list(df["target_end_date"].drop_duplicates())
    else:
        flu_ts = None
    scenario_int = list()
    for i in scenario:
        scenario_int.append(int(i))
    pathogen_data = {pathogen: {"data": df, "scenario_int": scenario_int, "time_series": flu_ts}}
    time_series_date = list()
    time_series_date.append(set(pathogen_data[pathogen]["time_series"]))
    for patho in other_pathogen:
        if other_scen[patho] is not None and len(other_scen[patho]) > 0:
            df_other = query_proj_data(location, target, "sample", other_pathogen_data[patho]["round_number"],
                                       path="./visualization/data-visualization/" + patho + "/")
            if df_other is not None:
                ts = list(df_other["target_end_date"].drop_duplicates())
                time_series_date.append(set(ts))
            else:
                ts = None
            other_scen_int = list()
            for i in other_scen[patho]:
                other_scen_int.append(int(
                    pathogen_set[patho]["scenario"]["dict"][i]))
        else:
            df_other = pd.DataFrame()
            ts = None
            other_scen_int = list()
        other_pathogen_data[patho].update({"data": df_other, "scenario_int": other_scen_int,
                                           "time_series": ts})
    time_series_date = set.intersection(*time_series_date)
    time_series_date = list(filter(None, list(time_series_date)))
    pathogen_info = pathogen_data | other_pathogen_data
    pathogen_information = {}
    for patho in list(pathogen_info.keys()):
        df_patho = pathogen_info[patho]["data"]
        if df_patho is not None and len(df_patho) > 0:
            df_patho = df_patho[df_patho["target_end_date"].isin(time_series_date)]
        df_patho = prep_pathogen_data(df_patho, pathogen_info[patho]["scenario_int"], patho.lower(), k=k)
        pathogen_information.update({patho: {"dataframe": df_patho}})
    df_all = prep_multipat_plot_comb(pathogen_information, calc_mean=True)
    # Observed data
    obs_other_patho = list()
    for patho in other_pathogen:
        if other_scen[patho] is not None:
            obs_other_patho.append(pathogen_set[patho]["display_name"])
    obs_data = multi_pathogen_obs_prep(round_tab, target, location, obs_other_patho, time_series_date)
    # Title & Subtitle
    title_pathogen = list()
    title_other_pathogen = list()
    for patho in other_pathogen:
        if other_scen[patho] is not None:
            if "round_display" in pathogen_set[patho].keys():
                round_name = pathogen_set[patho]["round_display"]
            else:
                round_name = other_pathogen_data[patho]["round_number"]
            disp_name = pathogen_set[patho]["display_name"]
            title_other_pathogen.append(disp_name)
            title_pathogen.append(disp_name + " (Round " + round_name + ")")
    title = (viz_setting[round_tab]["target"][target] + " - " + location + " (" + pathogen_disp_name + " (" +
             round_tab + "), " + ", ".join(title_pathogen) + ") ")
    scen_text = list()
    other_scen_text = list()
    if len(scenario) > 0:
        for i in scenario:
            scen_name = constant_dict["scenario_id"][str(i)]
            scen_name = re.search("^[A-Z]", scen_name)[0]
            scen_text.append(scen_name)
        scen_text = ", ".join(scen_text)
    else:
        scen_text = "no scenario selected"
    for patho in other_pathogen:
        other_path_scen_text = list()
        if other_scen[patho] is not None and len(other_scen[patho]) > 0:
            for i in other_scen[patho]:
                scen_name = re.search("^[A-Z]", str(i))[0]
                other_path_scen_text.append(scen_name)
            other_scen_text.append(pathogen_set[patho]["display_name"] + ": Scenario " +
                                   ", ".join(other_path_scen_text))
        elif other_scen[patho] is not None:
            other_scen_text.append(pathogen_set[patho]["display_name"] + ": " + "no scenario selected")
        else:
            other_scen_text.append(pathogen_set[patho]["display_name"] + ": " + "no projection available")
    title = (title + "<br><span style='font-size:14px'>" + pathogen_disp_name + ":  Scenario " + scen_text + "; " +
             "; ".join(other_scen_text) + "</span>")
    # Output
    prep_plot = {"df_all": df_all, "df_gs_data": obs_data["df_gs_data"], "title": title, "peaks": obs_data["peaks"],
                 "truth_legend": pathogen_disp_name + " Observed Data",
                 "target": viz_setting[round_tab]["target"][target],
                 "truth_tot_legend": pathogen_disp_name + " + " + " + ".join(title_other_pathogen).title() +
                 " Observed Data"}
    return prep_plot


@cache.memoize(timeout=TIMEOUT)
def draw_scenario_plot(scenario, location, target, ui, age_group, ens_check, round_tab, w_delay=6):
    if len(scenario) < 1:
        fig = fig_error_message("No scenario selected to display")
    else:
        prep_scen = scenario_plot_prep(scenario, location, target, ui, age_group, ens_check, round_tab)
        target_dict = viz_setting[round_tab]["target"]
    # Plot
        if (prep_scen["df"] is None) or (len(prep_scen["df"]) == 0):
            fig = fig_error_message("No projection to display for the target: " + target_dict[target] + ", location: " +
                                    str(location) + "; please select other options")
        else:
            df = prep_scen["df"].drop("horizon", axis=1)
            fig = make_scatter_plot(df, prep_scen["df_gs_data"], intervals=prep_scen["intervals"],
                                    x_title=prep_scen["x_title"], y_title=prep_scen["y_title"],
                                    subplot_var="scenario_id", hover_text=prep_scen["hover_text"],
                                    ensemble_name=prep_scen["ensemble_name"], title=prep_scen["title"],
                                    ensemble_color=prep_scen["ensemble_color"], h_lines=prep_scen["h_lines"],
                                    ensemble_view=prep_scen["ensemble_view"], color_dict=prep_scen["color_dict"],
                                    subplot_title=prep_scen["subplot_title"], point_value=prep_scen["point_value"],
                                    truth_data_type=prep_scen["truth_data_type"], share_x="all", share_y="all",
                                    zoom_in_projection=prep_scen["zoom_in_projection"], v_lines=prep_scen["v_lines"],
                                    truth_legend_name=prep_scen["truth_legend_name"], w_delay=w_delay)
            fig.update_layout(legend_itemsizing="constant")
            fig.update_layout(title=dict(yref='container', yanchor="bottom", pad=dict(b=0.5)))
        if viz_setting[round_tab]["scenario_plot"]["notes"] is not None:
            annotations = viz_setting[round_tab]["scenario_plot"]["notes"]["text"]
            annotations_str = str("<br>").join(annotations)
            fig.update_layout(legend={"title": {"text": annotations_str + "<br>", "side": "top"}})
    fig.add_annotation(
        x=0, y=1, xref="paper", yref="paper", text="&#9432;", font=dict(size=32), arrowcolor="white",
        arrowhead=False,
        hovertext="The RSV-NET hospitalization data plotted here as observations are preliminary and subject to change "
                  "<br>as more data become available. The number of recent hospitalizations can be affected by "
                  "<br>reporting lags and are thus backfilled sometimes. To account for this, the most recent 6 weeks "
                  "<br>of RSV-NET data are presented with points in a lighter shade of gray. "
                  "<br><br> Vertical Lines: <br> - gray full line: Start Projection Epiweek <br>"
                  " - gray dash line: Current Date")
    return fig


@cache.memoize(timeout=TIMEOUT)
def draw_spaghetti_plot(scenario, location, target, age_group, n_sample, med_plot, round_tab):
    prep_plot = spaghetti_plot_prep(scenario, location, target, age_group, n_sample, med_plot, round_tab)
    if (prep_plot["df"] is None) or (len(prep_plot["df"]) == 0):
        fig = fig_error_message("No projection to display for the target: " + prep_plot["y_title"] + ", location: " +
                                location + "; please select other options")
    elif len(scenario) < 1:
        fig = fig_error_message("No scenario selected to display")
    else:
        if med_plot is not None and med_plot == [True]:
            fig = make_spaghetti_plot(prep_plot["df"], subplot=True, subplot_col="scenario_id",
                                      color_dict=prep_plot["color_dict"], opacity=prep_plot["opacity"],
                                      add_median=True, title=prep_plot["title"], x_title="Epiweek",
                                      subplot_titles=prep_plot["subplot_titles"], y_title=prep_plot["y_title"],
                                      legend_dict=constant_dict["model_name"])
        else:
            fig = make_spaghetti_plot(prep_plot["df"], subplot=True, subplot_col="scenario_id",
                                      color_dict=prep_plot["color_dict"], opacity=prep_plot["opacity"],
                                      title=prep_plot["title"], subplot_titles=prep_plot["subplot_titles"],
                                      y_title=prep_plot["y_title"], x_title="Epiweek",
                                      legend_dict=constant_dict["model_name"])
        fig.add_annotation(
            x=0, y=1, xref="paper", yref="paper", text="&#9432;", font=dict(size=32), arrowcolor="white",
            arrowhead=False,
            hovertext="This plot represents weekly epidemic trajectories simulated by different models (by default, " 
                      "<br>10 trajectories are plotted for each model ). These should be understood as the raw outputs"
                      " <br>from each model. Variation between trajectories of the same model is driven by model <br>"
                      "uncertainty, which can take different forms, including parametric uncertainty <br> "
                      "(eg, uncertainty about transmission or immunity or other assumed model parameters) and/or <br>"
                      "stochasticity (eg stochastic models such as agent-based approaches will return different <br>"
                      "outputs for the same set of parameters). Based on these raw trajectories, probabilistic <br>"
                      "distributions for incident and cumulative hospitalizations are generated. Additional"
                      " <br>targets such as peak timing and size can also be estimated. All of the other tabs represent"
                      " <br> probabilistic distributions that are derived from these raw trajectories.")
        fig.update_layout(legend_itemsizing="constant")
    return fig


@cache.memoize(timeout=TIMEOUT)
def draw_specific_plot(model, location, target_type, ui, age_group, round_tab):
    prep_spec = specific_plot_prep(model, location, target_type, ui, age_group, round_tab)
    # Plot
    if (prep_spec["df"] is None) or (len(prep_spec["df"]) == 0):
        fig = fig_error_message("No projection to display for the Model: " + str(model) + ", Location: " +
                                str(location) + "; please select other options")
    else:
        fig = make_scatter_plot(prep_spec["df"], prep_spec["df_gs_data"], subplot_var="target", line_width=4,
                                legend_col="scenario_id", x_title="Epiweek", y_title="",  title=prep_spec["title"],
                                point_value=prep_spec["point_value"], intervals=prep_spec["intervals"],
                                subplot_title=prep_spec["subplot_title"], share_x=False, share_y=False,
                                legend_dict=prep_spec["legend_dict"], palette="Portland",
                                hover_text="%{scenario_id}<br>", truth_mode="markers")
    return fig


@cache.memoize(timeout=TIMEOUT)
def draw_comparison_plot(location, age_group, multi_ref, round_tab):
    prep_comp = comparison_plot_prep(location, age_group, multi_ref, round_tab)
    # Plot
    if prep_comp["df"] is None:
        fig = fig_error_message("No projection to display for the Location: " +
                                str(location) + "; please select other options")
    else:
        fig = make_point_comparison_plot(prep_comp["df"], prep_comp["ens_name"], prep_comp["comparison"],
                                         style="individual", subplot=True, title=prep_comp["title"],
                                         subplot_titles=prep_comp["subplot_title"],
                                         subplot_col="comparison",  color_dict=constant_dict["color_dict"])
        fig.update_layout(legend_orientation="h")
        fig.update_xaxes(showticklabels=False)
    return fig


@cache.memoize(timeout=TIMEOUT)
def draw_peak_time(scenario, model, order, round_tab):
    if len(scenario) < 1:
        fig = fig_error_message("No scenario selected to display")
    else:
        prep_plot = peak_time_prep(scenario, model, order, round_tab)
        if len(prep_plot["df"]) > 0:
            fig = make_heatmap_plot(prep_plot["df"], subplot=True, subplot_col="scenario_id",
                                    subplot_titles=prep_plot["subplot_title"], title="Hospitalization Peak Timing")
            fig.add_annotation(
                x=0, y=1, xref="paper", yref="paper", text="&#9432;", font=dict(size=32), arrowcolor="white",
                arrowhead=False,
                hovertext="A probability of 1 in the first week of the projection period could mean either future  <br>"
                          "projections are not expected to exceed a prior peak or projections expect the peak will <br>"
                          "occur in the first week."
                          "<br><br> Vertical Line: Current Date")
            fig.add_vline(x=datetime.today().strftime('%Y-%m-%d'), line_width=2, line_color="gray", line_dash="dash")
        else:
            fig = fig_error_message("No projection to display; please select other options")
    return fig


@cache.memoize(timeout=TIMEOUT)
def draw_peak_size(scenario, location, round_tab):
    if len(scenario) < 1:
        fig = fig_error_message("No scenario selected to display")
    else:
        prep_plot = peak_size_prep(scenario, location, round_tab)
        if len(prep_plot["df"]) > 0:
            fig = make_boxplot_plot(prep_plot["df"], subplot=True, subplot_col="scenario_id",
                                    subplot_titles=prep_plot["subplot_title"], color_dict=prep_plot["color_dict"],
                                    share_x=False,  sub_orientation=None, sub_nrow=None,
                                    box_value=[0.025, 0.25, 0.5, 0.75, 0.975], subplot_spacing=0.1,
                                    title="Hospitalization Peak Size (" + location + ")")
        else:
            fig = fig_error_message("No projection to display; please select other options")
    return fig


@cache.memoize(timeout=TIMEOUT)
def draw_multi_pathogen_comb_plot(location, target, scenario, other_scen, round_tab, err_bar):
    if None in list(other_scen.values()) and len(other_scen.values()) > 0:
        scen_other_len = list(filter(None, list(other_scen.values())))
        if len(scen_other_len) > 0:
            scen_other_len = len(list(np.concatenate(scen_other_len)))
        else:
            scen_other_len = len(scen_other_len)
    else:
        scen_other_len = len(list(np.concatenate(list(other_scen.values()))))
    if len(scenario) < 1 and scen_other_len < 1:
        fig = fig_error_message("No scenario selected to display")
    else:
        color = constant_dict["pathogen_color_dict"]
        other_pathogen = list()
        for patho in other_scen.keys():
            if other_scen[patho] is not None and len(other_scen[patho]) >= 1:
                other_pathogen.append(viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho]["display_name"])
        prep_plot = multi_pathogen_combined_prep(location, target, scenario, other_scen, round_tab)
        df_all = prep_plot["df_all"]
        if prep_plot["df_gs_data"] is not None:
            truth_data = prep_plot["df_gs_data"]
        else:
            truth_data = None
        fig = make_combine_multi_pathogen_plot(
            df_all, [constant_dict["pathogen_display_name"]] + other_pathogen,  title=prep_plot["title"],
            y_axis_title=prep_plot["target"], truth_data=truth_data, bar_calc="mean", color=color,
            error_bar_pat=err_bar)
        if None not in prep_plot["peaks"]:
            for peak_dict in prep_plot["peaks"]:
                if peak_dict["value"] is not None and ~np.isnan(peak_dict["value"]):
                    fig = fig.add_hline(y=int(peak_dict["value"]), line_width=1, line_color="black", line_dash="dash",
                                        annotation=dict(font_size=10, font_color="black"),
                                        annotation_position="top left", row=1,
                                        annotation_text=peak_dict["name"] + ": " + str(int(peak_dict["value"])))
        title_pathogen = list()
        for patho in other_pathogen:
            if "round_display" in viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho.lower()].keys():
                round_name = ("Round" +
                              viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho.lower()]["round_display"])
            else:
                round_name = viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho.lower()]["round"].title()
            title_pathogen.append(patho + " (" + round_name + ")")
        if "notes" in viz_setting[round_tab]["multi-pathogen_plot"]:
            fig.add_annotation(x=0, y=-0.075, text="".join(viz_setting[round_tab]["multi-pathogen_plot"]["notes"]),
                               xref="paper", yref="paper", arrowhead=False, arrowcolor="white", xanchor="left",
                               yanchor="top")
        fig.add_annotation(
            x=0, y=1, xref="paper", yref="paper", text="&#9432;", font=dict(size=32), arrowcolor="white",
            arrowhead=False,
            hovertext="These projections are generated by combining randomly sampled " +
                      constant_dict["pathogen_display_name"] + " " + round_tab + " "
                      "<br>trajectories with randomly sampled " + ", ".join(title_pathogen) + " trajectories. "
                      "<br>Sampling is weighted to ensure equal likelihood of sampling from the contributing models. "
                      "<br>Quantiles are generated from 10 000 of these combined trajectories. For each combined "
                      "<br>trajectory, we calculated the weekly proportion of overall burden that comes from each "
                      "<br>pathogen. We summarized these proportions with a mean and 50% uncertainty interval. <br>"
                      "<br>The observed data used in this plot comes from different sources and surveillance systems. "
                      "<br>Flu & COVID-19 hospitalization data comes from the `Weekly reported state-level incident<br>"
                      " hospitalizations`, based on HHS COVID and Flu reporting system; and RSV comes from the <br>"
                      "RSV-NET surveillance system.")
    return fig


@app.callback(Output("round_tabs-content", "children"),
              Input("tabs-round", "value"))
def render_round_content(round_tab):
    tab_list = viz_setting[round_tab]["plot_tab"]
    return html.Div([
        html.Div([
            html.Div("", id="sidebar"),
            make_tab_plots(tab_list, tab_name_dict)
        ], className="row"),
        html.Hr(className="hr-notes"),
        make_notes_definition(definition, left_note, right_note)
    ])


@app.callback(Output("scenario-round_tabs-content", "children"),
              Input("tabs-round", "value"))
def render_scenario_content(round_tab):
    round_number = viz_setting[round_tab]["round_number"]
    filename = "visualization/data-visualization/scenario_info/scenario_round" + str(round_number) + ".md"
    with open(filename, "r") as f:
        markdown_text = f.read()
    return html.Div([
        dcc.Markdown(markdown_text)
    ])


@app.callback(Output("metadata-round_tabs-content", "children"),
              Input("tabs-round", "value"))
def render_metadata_content(round_tab):
    if round_tab == "General Model Information":
        output = make_dt_metadata(metadata_file)
    else:
        round_number = viz_setting[round_tab]["round_number"]
        output = make_abstract_tab(str(round_number))
    return output


@app.callback(Output("abstract-output", "children"),
              Input("tabs-round", "value"),
              Input("abstract-dropdown", "value"))
def render_abstract_content(round_tab, team_model_name):
    round_number = viz_setting[round_tab]["round_number"]
    abs_content = render_abstract(str(round_number), viz_setting[round_tab]["date_round"], team_model_name)
    return abs_content


@app.callback(
    Output("sidebar", "children"),
    Input("tabs-plot", "value"),
    Input("tabs-round", "value"))
def render_sidebar_content(plot_tab, round_tab):
    round_number = viz_setting[round_tab]["round_number"]
    scenario_dict = constant_dict["scenario_id"]
    if "unselect_scenario" in viz_setting[round_tab].keys():
        unselect_scen = viz_setting[round_tab]["unselect_scenario"]
    else:
        unselect_scen = None
    target_dict = viz_setting[round_tab]["target"]
    def_target = viz_setting[round_tab]["def_target"]
    cumulative = True
    ui_value = 95
    if plot_tab == "multipat_plot_comb":
        unselect_scen = viz_setting[round_tab]["multi-pathogen_plot"]["unselect"]
    if viz_setting[round_tab]["multi"] == "True":
        multi_ui = True
        if plot_tab == "scenario":
            ui_value = -1
    else:
        multi_ui = False
    if 'risk_map' in viz_setting[round_tab].keys():
        if viz_setting[round_tab]["risk_map"]["cumulative"] == "False":
            cumulative = False
    return make_sidebar(round_number, plot_tab, scen_file, location_rsv, scenario_dict, target_dict, def_target,
                        age_group=viz_setting[round_tab]["age_group"], ui_val=ui_value,
                        unselect_scenario=unselect_scen, cumulative=cumulative, multi_ui=multi_ui,
                        round_name=round_tab)


@app.callback(
    Output("plot_tabs-content", "children"),
    Input("tabs-plot", "value"),
    Input("tabs-round", "value"))
def render_plot_tab_content(plot_tab, round_tab):
    # Prepare graph
    graph = dcc.Loading(id="loading_plot", type="circle", children=[
        dcc.Graph(id=plot_tab + "-graph", config={"doubleClick": "reset"})
    ])
    # Prepare plot bar
    ens_def = viz_setting[round_tab]["ensemble"]["default"]
    max_horizon = viz_setting[round_tab]["horizon_limit"]["required"]
    if viz_setting[round_tab]["ensemble"]["hide"] is None:
        hide_ens = True
    else:
        hide_ens = False
    if "multi_panel" in viz_setting[round_tab]["scenario_comparison"]:
        sc_panel = list(viz_setting[round_tab]["scenario_comparison"]["multi_panel"].keys())
        sc_multi_panel = True
    else:
        sc_panel = list(viz_setting[round_tab]["scenario_comparison"].keys())
        sc_multi_panel = False
    if "sidebar_option" in viz_setting[round_tab]["scenario_comparison"]:
        sc_sidebar_option = True
    else:
        sc_sidebar_option = False
    pathogen = constant_dict["pathogen_display_name"]
    scen_information = scen_df[scen_df["round"] == "round" + str(viz_setting[round_tab]["round_number"])]
    scen_choice = scen_information["scenario_id"].tolist()
    radio = None
    if "multi-pathogen_plot" in viz_setting[round_tab]:
        other_pathogen = list()
        radio_error_bar_list = [constant_dict["pathogen_display_name"]]
        for patho in viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"]:
            pathogen_information = viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho]
            patho_scen_sel = list()
            for i in range(len(pathogen_information["scenario"]["name"])):
                patho_scen_sel.append(pathogen_information["scenario"]["id"][i] + " (" +
                                      pathogen_information["scenario"]["name"][i] + ")")
            patho_scen_dict = {"id": pathogen_information["scenario"]["id"], "name": patho_scen_sel}
            def_scen = pathogen_information["default_selection"]
            if "round_display" in pathogen_information.keys():
                patho_round = pathogen_information["round_display"]
            else:
                patho_round = pathogen_information["round"]
                patho_round = int(re.sub("\D", "", patho_round))
            patho_website = pathogen_information["website"]
            patho_dic = {"scenario": patho_scen_dict, "default_sel": def_scen, "round_int": patho_round,
                         "name": pathogen_information["display_name"], "website": patho_website}
            other_pathogen.append(patho_dic)
            radio_error_bar_list.append(
                viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho]["display_name"])
        if plot_tab == "multipat_plot_comb":
            radio = html.Div([
                html.Span("Error bar: "),
                dcc.RadioItems(radio_error_bar_list, radio_error_bar_list[0], inline=True, id="comb_err_radio")
            ], className="err_bar")
    else:
        other_pathogen = None
    plot_bar = make_plot_bar(ens_def, max_horizon, hide_ens, sc_panel, sc_multi_panel, sc_sidebar_option, pathogen,
                             scen_choice, other_pathogen, plot_tab)
    # output plot tab
    return html.Div([plot_bar, graph, radio])


@app.callback(
    Output("model_dropdown", "options"),
    Input("tabs-round", "value"),
    Input("ensemble-checkbox", "value"))
def render_model_dropdown_content(round_tab, ens_check):
    model_list = viz_setting[round_tab]["models"]
    model_list = list(set(model_list))
    if (ens_check != ['True']) and (viz_setting[round_tab]["ensemble"]["hide"] is not None):
        for j in viz_setting[round_tab]["ensemble"]["hide"]:
            model_list.remove(j)
    return sorted(model_list)


@app.callback(
    Output("html-table", "children"),
    Input("tabs-round", "value"),
    Input("tabs-plot", "value"))
def update_html_table(round_tab, plot_tab):
    round_number = viz_setting[round_tab]["round_number"]
    file_name = "./assets/scenario_table/round" + str(round_number) + ".html"
    if os.path.isfile(file_name):
        if plot_tab in ["multipat_plot", "multipat_plot_comb"]:
            pathogen_name = list(viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"].keys())
            if plot_tab == "multipat_plot":
                pathogen_name = [pathogen_name[0]]
            file_list = [dcc.Tab(label=constant_dict["pathogen_display_name"], children=[
                            html.Div([html.Embed(src=file_name, className="scenario_table")])
                        ])]
            for patho in pathogen_name:
                other_file_name = ("./assets/scenario_table/" + patho.lower() + "/" +
                                   viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho]["round"] + ".html")
                if os.path.isfile(other_file_name):
                    file_list.append(dcc.Tab(
                                children=[html.Div([html.Embed(src=other_file_name, className="scenario_table")])],
                                label=viz_setting[round_tab]["multi-pathogen_plot"]["pathogen"][patho]["display_name"]))

            return html.Div([
                    dcc.Tabs(parent_className="plot_tabs", className='plot_tabs-container', children=file_list)
                ])
        else:
            return html.Div([
                    html.Embed(src=file_name, className="scenario_table")
                ])
    else:
        return html.Div()


@app.callback(
    Output("scenario-graph", "figure"),
    Input("location-dropdown", "value"),
    Input("target-radio", "value"),
    Input("scenario-checklist", "value"),
    Input("ui-radio", "value"),
    Input("age_group-radio", "value"),
    Input("tabs-round", "value"),
    Input("ensemble-checkbox", "value"))
def scenario_plot(location, target, scenario, ui, age_group, round_tab, ens_check):
    tic = time.perf_counter()
    fig = draw_scenario_plot(scenario, location, target, ui, age_group, ens_check, round_tab)
    toc = time.perf_counter()
    print(f"Draw Scenario plot in {toc - tic:0.4f} seconds")
    return fig


@app.callback(
    Output("spaghetti-graph", "figure"),
    Input("location-dropdown", "value"),
    Input("target-radio", "value"),
    Input("scenario-checklist", "value"),
    Input("age_group-radio", "value"),
    Input("sample-slider", "value"),
    Input("median-checkbox", "value"),
    Input("tabs-round", "value"))
def spaghetti_plot(location, target, scenario, age_group, n_sample, med_plot, round_tab):
    tic = time.perf_counter()
    fig = draw_spaghetti_plot(scenario, location, target, age_group, n_sample, med_plot, round_tab)
    toc = time.perf_counter()
    print(f"Draw Spaghetti plot in {toc - tic:0.4f} seconds")
    return fig


@app.callback(
    Output("model_specific-graph", "figure"),
    Input("location-dropdown", "value"),
    Input("ui-radio", "value"),
    Input("model_dropdown", "value"),
    Input("target_type-radio", "value"),
    Input("age_group-radio", "value"),
    Input("tabs-round", "value"))
def model_specific_plot(location, ui, model, target_type, age_group, round_tab):
    tic = time.perf_counter()
    fig = draw_specific_plot(model, location, target_type, ui, age_group, round_tab)
    toc = time.perf_counter()
    print(f"Draw the Model Specific plot in {toc - tic:0.4f} seconds")
    return fig


@app.callback(
    Output("scen_comparison-graph", "figure"),
    Input("location-dropdown", "value"),
    Input("age_group-radio", "value"),
    Input("multi-ref", "value"),
    Input("tabs-round", "value"))
def scen_comparison_plot(location, age_group, multi_ref, round_tab):
    tic = time.perf_counter()
    fig = draw_comparison_plot(location, age_group, multi_ref, round_tab)
    toc = time.perf_counter()
    print(f"Draw Scenario Comparison plot in {toc - tic:0.4f} seconds")
    return fig


@app.callback(
    Output("peak_time_model-graph", "figure"),
    Input("scenario-checklist", "value"),
    Input("model_dropdown", "value"),
    Input("order_heatmap", "value"),
    Input("tabs-round", "value"))
def peak_time_plot(scenario, model, order, round_tab):
    tic = time.perf_counter()
    fig = draw_peak_time(scenario, model, order, round_tab)
    toc = time.perf_counter()
    print(f"Draw Peak time plot in {toc - tic:0.4f} seconds")
    return fig


@app.callback(
    Output("peak_size-graph", "figure"),
    Input("scenario-checklist", "value"),
    Input("location-dropdown", "value"),
    Input("tabs-round", "value"))
def peak_time_plot(scenario, location, round_tab):
    tic = time.perf_counter()
    fig = draw_peak_size(scenario, location, round_tab)
    toc = time.perf_counter()
    print(f"Draw Peak size plot in {toc - tic:0.4f} seconds")
    return fig


@app.callback(
    Output("multipat_plot_comb-graph", "figure"),
    Input("scenario-checklist", "value"),
    Input("location-dropdown", "value"),
    Input("target-radio", "value"),
    Input("tabs-round", "value"),
    Input("other-scenario_covid-19", "value"),
    Input("other-scenario_flu", "value"),
    Input("comb_err_radio", "value"), prevent_initial_call=True)
def multipat_comb_plot(scenario, location, target, round_tab, other_scen1, other_scen2, err_bar):
    tic = time.perf_counter()
    other_scen = {"covid-19": other_scen1, "flu": other_scen2}
    fig = draw_multi_pathogen_comb_plot(location, target, scenario, other_scen, round_tab, err_bar)
    toc = time.perf_counter()
    print(f"Draw Multi Pathogen Combined plot in {toc - tic:0.4f} seconds")
    return fig


# Run ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="3838", debug=False)
