# Scenario Modeling Hub - Example

This repository is **in development**.

This repository serves to store example data for scenario modeling hub round, 
modeled after the US Scenario Modeling Hub.

## Folder documentation

- Auxiliary data: Additional files: for example here, location information
(name, FIPS code, population)
- Hub Config: 
    - `tasks.json` JSON files containing the description of the round, following
the hubverse standard (
[hubverse documentation](https://hubverse.io/en/latest/user-guide/hub-config.html#hub-model-task-configuration-tasks-json-file))
    - `constant.json` & `viz_settings.json`: JSON files associated with the 
    visualization
- Model output: Example of submission files from 4 different to a US SMH round
- Output Processed: Example of internal "processed" files generated for a round
using model output files: calculate additional targets, and ensembles
- Visualization: examples of files used for visualization, generated from the 
"processed" files.
    - data-goldstandard: observed data (here, incident and cumulative hospitalization)
    - data-visualization: 
        - models: per each round (here round 1), partitioned by target, location,
        output type: team-model and ensemble projection 
        - scenario info: `.MD` containing the description of the round
        - `scenario_round_info.csv`: CSV containing the scenario description
        for each round: ID, round ID, Short and Full Name.


## Visualization projection files

### Column description:

- `value`: value
- `type_id`: output type id, for example quantile value or sample ID
- `model_name`: team-model or ensemble in a numeric format (translation in 
`constant.json`)
- `target_end_date`: date
- `scenario_id`: scenario id in a numeric format (translation in 
`constant.json`) 
- `horizon`: horizon
- `location`: location in FIPS code
- `age_group`: age group

## Run local visualization

### Folder Description

The visualization information is separated into multiple folders and files:

- `assets` containing the CSS, HTMLs scenario tables files for the Dash App.
- `data-locations` containing location and population size information.
- `pages` containing the "templates" Python scripts of each page of the Dash App.
- `plots` containing the additional scripts specific to this the Dash App.
- `utils` containing specific utils Python functions used in the Dash App.
- `visualization` containing all the output data used for the visualization.
- `main.py` contains the Python code to run the Dash app.
- `settings.py` contains round related information and settings information for the Dash App.

### Run Locally

The requirements from the website are available in the requirements.txt file

```
brew install conda
cd to project directory
conda create --name flu-scenario-hub_pywebsite
conda activate flu-scenario-hub_pywebsite
conda install plotly
conda install pandas
pip install pyarrow
pip install polars
conda install dash
conda install -c conda-forge flask-caching
python main.py
```
To install SMH specific library from GitHub:

`pip install git+https://github.com/midas-network/SMHViz_layout`
`pip install git+https://github.com/midas-network/SMHViz_plot`


## Data license and reuse

All source code that is specific to the overall project is available under an open-source MIT license. 
We note that this license does NOT cover model code from the various teams or model scenario data 
(available under specified licenses).

## Funding

Scenario modeling groups are supported through grants to the contributing investigators.

The Scenario Modeling Hub cite is supported by the MIDAS Coordination Center, NIGMS Grant U24GM132013 
to the University of Pittsburgh.
