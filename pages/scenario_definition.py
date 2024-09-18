import dash
from dash import html, dcc

from settings import viz_setting
from SMHviz_layout.tabs import make_round_tab

# Settings ---
list_round = list(viz_setting.keys())
round_tab_list = make_round_tab(list_round)

# page
dash.register_page(__name__, name="Scenario Definition")

# layout
layout = html.Div([
    html.H4(''),
    html.Div([
        dcc.Tabs(id="tabs-round", value=list_round[-1], parent_className="round_tabs",
                 className='round_tabs-container', children=round_tab_list),
        html.Br(),
        html.Div(id="scenario-round_tabs-content")
    ])
])
