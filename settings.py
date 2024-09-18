import json
import pandas as pd
from dash import html

# Plot tab dictionary
tab_name_dict = {
    "spaghetti": "Individual Trajectories",
    "scenario": "Scenario Plot",
    "model_specific": "Model Specific Plot",
    "scen_comparison": "Scenario Comparison",
    "model_distribution": "Model Distribution",
    "multipat_plot": "Multi-Pathogen Plot",
    "multipat_plot_comb": "Multi-Pathogen Combined Plot",
    "peak_time_model": "Hospitalization Peak Timing",
    "peak_size": "Hospitalization Peak Size"
}

# ui dictionary
ui_dict = {
    -1: [0.025, 0.975, 0.05, 0.95, 0.1, 0.9, 0.25, 0.75, 0.5],
    0: [0.5],
    95: [0.025, 0.975, 0.5],
    50: [0.250, 0.750, 0.5]
}


# Location list
location_file = "./data-locations/locations.csv"
location_info = pd.read_csv(location_file)
location_rsv = location_info[location_info["location"].isin([
    "US", "06", "08", "09", "13", "24", "26", "27", "35", "36", "41", "47", "49"])]

# Scenario
scen_file = "./visualization/data-visualization/scenario_round_info.csv"
scen_df = pd.read_csv(scen_file)

# Model path
metadata_file = "./visualization/data-visualization/models/model_description.csv"

# JSON constant information
json_path = "./hub-config/constant.json"
# read file
with open(json_path, 'r') as json_file:
    data = json_file.read()
# parse file
constant_dict = json.loads(data)

invert_team_name = {v: k for k, v in constant_dict["model_name"].items()}
invert_scenario_id = {v: k for k, v in constant_dict["scenario_id"].items()}

# JSON round information
json_path = "./hub-config/viz_settings.json"
# read file
with open(json_path, 'r') as json_file:
    data = json_file.read()
# parse file
viz_setting = json.loads(data)

# Notes
definition = html.Div([
    html.Span("Please consult the "),
    html.A("Metadata Page", href="./model-metadata"),
    html.Span(" for more details on the different ensemble approaches and individual models."),
    html.Br(), html.Br(),
    html.B("Epiweek: "),
    html.Span("Epidemiological Week as defined by MMWR"),
    html.Br(), html.Br(),
    html.B("LOP: "),
    html.Span("Linear Opinion Pool; method used to calculate `Ensemble_LOP` and `Ensemble_LOP_untrimmed` by " 
              "averaging cumulative probabilities of a given value across submissions. See Notes at the "
              "bottom of the page, for more details. ")
    ])

left_note = html.Div([
    html.U([html.B("Ensemble methods:")]),
    html.Span(" The Scenario Modeling Hub ensembles individual projections using two methods :"),
    html.Div(["(a) ", html.B("Ensemble_LOP"),
              html.Span(" is calculated by averaging cumulative probabilities of a given value across weighted "
                        "submissions. At each  value, the highest and lowest probability is removed before averaging.")
              ]),
    html.Div(["(b) ", html.B("Ensemble_LOP_untrimmed"),
              html.Span(" is calculated by averaging cumulative probabilities of a given value across weighted "
                        "submissions. All values are included in the average.")
              ]),
    html.Div(["(c) ", html.B("Ensemble"),
              html.Span(" is obtained by calculating the weighted median of each submitted quantile.")
              ]),
    html.Br(),
    html.Div(["Ensembles projection include only those submissions that reported all scenarios "
              "for their targets. Individual model and ensemble projections are available in the ",
              html.A("GitHub Repository", target="blank",
                     href="https://github.com/midas-network/rsv-scenario-modeling-hub")]),
    html.Br()
])

right_note = html.Div([
    html.Div(),
    html.Br(),
    html.Div([html.U([html.B("Licensing:")]),
              html.Span(" Models projection are available by default under a CC BY 4.0 license. Some models have "
                        "specific license. See repository for details.")]),
    html.Br(),
    html.Div([
        html.U([html.B("Disclaimer:")]),
        html.Span("  The content of the app is solely the responsibility of the "
                  "participating teams and the Hub maintainers and does not represent the official views of any "
                  "related funding organizations.")
    ])
])
