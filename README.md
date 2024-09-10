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
