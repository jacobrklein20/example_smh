import dash
from dash import dcc
from settings import *
from SMHviz_layout.tabs import make_round_tab

# Settings
list_round = list(viz_setting.keys())
list_abstract = list(["General Model Information"])
for i in list_round:
    if viz_setting[i]["abstract"] == "True":
        list_abstract.append(i)
round_tab_list = make_round_tab(list_abstract)


dash.register_page(__name__, name="Model Metadata")

layout = html.Div([
    html.H4(''),
    html.Div([
        dcc.Tabs(id="tabs-round", value=list_abstract[0], parent_className="round_tabs",
                 className='round_tabs-container', children=round_tab_list),
        html.Br(),
        html.Div(id="metadata-round_tabs-content")
    ])
])
