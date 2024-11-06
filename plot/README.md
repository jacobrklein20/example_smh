# Scenario Modeling Hub - Example - Plot documentation

This repository is **in development**.

This repository serves to store example data for scenario modeling hub round, 
modeled after the US Scenario Modeling Hub.

## Multi-pathogen combined plot

**Only for rounds with individual trajectories as required output.**
 
### Workflow:

Depending on the location, target and scenario selected (scenario for each pathogen):

For example: 
- Location: US
- Target: Incident Hospitalization
- Scenario Pathogen I (PI): C and D
- Scenario Pathogen II (PII):  D
- Scenario Pathogen III (PIII): A and B
- Number of Sample (k): 10 000


1. Load all the individual trajectories for each pathogen for a specific 
location and target
2. Restrict the time series of each trajectories to the common time series 
between all the pathogens. For example if PI projections are from Sept1 to Dec1 and PII, PIII 
from July1 to Nov1, only Sept1 to Nov1 will be selected.
3. For each pathogen:
    - Create a `"sample_id"` variable corresponding to the concatenation
     `<model_name>_<output_type_id><scenario_id>`
    - For each team_model:
        - create a `"list_sample"`: list of all the possible "sample_id" associated with 
        the team_model. For example: "modelA_1_scenC", "modelA_2_scenC", etc.
        - create a `"list_weight"`` : list of all each weight associated with each "sample_id". 
        Calculated as: 1 / total number of trajectories of the specific location, target, 
        scenario, model_team.
        For example: 1/100, 1/100, etc
    - Concatenate all the list for each team_model together. For example:
        - `list_sample = "modelA_1_scenC", "modelA_2_scenC", …, "modelA_100_scenC", 
        "modelB_1_scenC", "modelB_2_scenC", … , "modelB_90_scenC"`, etc.
        - `list_weight = 1/100, 1/100, …, 1/100, 1/90, 1/90, …, 1/90`, etc.
    - Transform the list_weigth to sum to 1 by dividing by the number of model_team and scenario 
    for the location, target. 
    For example (if we have 2 model team for US, Incident Hospitalization, Flu):
    `list_weight = (1/100)/2, (1/100)/2, …, (1/100)/2, (1/90)/2, (1/90)/2, …, (1/90)/2`.
    `list_weight = list_weight/number of scenario`
    - Sample the list_sample X times with the associated weight and with replacement, by applying:
        `sample = np.random.choice(list_sample, p=weight_sample_fin, size=k, replace=True)`
        k parameter defined by the Hub (here: 10000)
    - Shuffle the list to avoid having the list ordered by scenario, model, trajectories id.
    - Select all the individual trajectories data frame input from the complete "sample" list. If a
    `sample_id` is sampled multiple times, it will be repeated multiple times in the output data frame.
    - Recode the `sample_id` to a numeric corresponding to 1 to number of sample (here: 10000)
    - Update the output to keep only a data frame with columns: `"date"`, `"value_<pathogen name>"`, `"sample_id"` 
4. Merge all the pathogen output data frame (step 3 output) together by using the common dates 
and sample_id information
5. For each row, calculate new column:
    - `"value"` = sum of of all the `"value_<pathogen name>"` column
    - `"proportion_<pathogen name>"` = `"value_<pathogen name>"` / `"value"`

### Plot:
Create one plot with 2 subplots:

#### Scatter plot
Scatte plot of 50%, 80%, 90% and 95% intervals of the "combined" and individual
pathogens projections

Calculate the quantiles for each date of the column value
Represent the 50%, 80%, 90% and 95% intervals (ribbons)

#### Bar plot

Bar blot of the contribution of each pathogen

Calculate the median value of each  `"proportion_<pathogen name>"` per date
Represent for each date a stacked bar, mean proportion of each pathogen.
For example
- color 1 : mean of `"proportion_PI"`
- color 2 : mean of `"proportion_PII"`
- color 3: mean of `"proportion_PIII"`
- Error bar for Flu: use 50% intervals of proportion_flu
