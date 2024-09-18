# Configuration files

These JSON files contain information to create the SMH visualization and need
to be updated each new rounds. 

## `constant`

JSON files containing general information about the SMH for the
visualization:

- `pathogen`: Name of the pathogen 
- `pathogen_display_name`: Display name of the pathogen 


- `scenario_id`: dictionary containing all the scenario id information
    (name and equivalent numeric) for all rounds

  
- `model_name`: dictionary containing all the team-model name information
    (name and equivalent numeric) for all rounds
- `color_dict`: dictionary containing the color information associated 
     with each team-name model

- `pathogen__color_dict`:  dictionary containing the color information associated 
     with each pathogen included in the website.
  
- `location_order`: list containing the order of the US states 
   for the heatmaps. The order follow the long/lat and CDC State
   group.

The `scenario_id ` and the `model_name` dictionary are used to translate input
model projection files use in the visualization containing this information
as numeric. **Please be careful when updating to keep the backward
compatibility.**


## `viz_settings`

JSON files containing detailed information by round about the SMH for the
visualization. Each round should contain multiple information organized by
round and named "Round X" and contains all sections:


- `round_number`: numeric, number of the round


- `date_round`: date (YYYY-MM-DD), date used to identify the
  round, "origin_date" in the submission file


- `show`: boolean or str, if "True" the tabs with all the plot will be
  included in the visualization, any other value will be printed instead of
  the plot tabs. For example, if "show": "Round not published", the
  text "Round not published" will be printed in the visualization instead of
  the plot tabs


- `plot_tab`: list, list of the name of the tabs to include in the
  visualization for this selection (in the order of the tab on the website): 
  - "spaghetti": "Individual Trajectories",
  - "scenario": "Scenario Plot",
  - "model_specific": "Model Specific Plot",
  - "scen_comparison": "Scenario Comparison",
  - "model_distribution": "Model Distribution",
  - "multipat_plot_comb": "Multi-Pathogen Combined Plot",
  - "peak_time_model": "Hospitalization Peak Timing",
  - "peak_size": "Hospitalization Peak Size"


- `target`: dict, name of the target included in this round with the name, as
  in the model projection field, as keys and, with the full name as value


- `age_group`: dict, name of the age group included in this round with the 
  name, as in the model projection field, as keys and, with the full name as 
  value


- `def target`: str, name or part of the name of the target to be selected by
  default in the visualization, the first `target` matching will be selected
  by default.


- `models`: list, list of team-model name participating in this specific 
   round


- `point`: dict, containing the information about the value to use as
  principal trait for all the plots:
  - By default, use median value: 
  ``` 
  "point": {"type": "quantile", "type_id": 0.5}
  ```


- `ensemble`: dict, containing the information about the ensembles with
  the "default" ensemble being used on all the plots and the "hide" ensembles
  being used only by selecting a checkbox on the visualization but exclude by
  default. If the input contains only one Ensemble, set the value associated
  with the "hide" key to `null`. If "hide" is not `null`, it should be a list


- `zeroed_file`: string, "True" if the round use zeroed file in the
  visualization, "False" if not, "Sample" if the input file have the 
  required input file format is "sample" and "quantile" optional. (use for 
  assigning "scenario comparison" calculation method)


- `horizon_limit`: dict, containing the "required" and "optional" horizon 
   limit for the round in number of week. Same value if no optional value. 


- `gold_standard`: dict, containing for each target (key, as in the model
  projection files) the corresponding name of the file stored in the
  `visualization/data-goldstandard/` folder to use for Observed Data. If no
  observed data is associated with the target, set the value to `null`


- `multi`:  boolean, "True" if the sidebar Uncertainty Interval RadioButtons
  need to include a "multi" options, "False" if not 


- `abstract`: boolean, "True" if a "Round X" tab need to be added in
  the "Model Metadata" page to include the abstracts for the corresponding
  round, "False" if not

Plot related sections can be added (optional if the plot does not appear in the round):

- `scenario_plot`: Information to add on the Scenario plot 
	- `peak`: dict, containing information for:
      - `"start_date"` and `"end_date"` and a peak name
      for one or multiple previous peaks defined by a specific time frame (if "end_date" 
      is null, ongoing time frame) and used to draw a horizontal red dotted line on the 
      scenario plot showing the maximum peak on this time frame. `null` is no peak 
      information on the plot. 
      - OR `"file_name"` and `"col_name"` and a threshold name or one or multiple threshold, 
      information should be stored by state (location name following the SMH standard) in
      a CSV files with the associated threshold in the column "col_name" (see Round 17 COVID-19 for
      example)
      - (optional) "target_specific": to include the peak or threshold only for a specific
      target (target name as in the submission file format)
      - Set to `null` is no peaks to add.
    - `notes`: dict, containing information:
      - `models`: list of models concerned by the notes (will add an asterix 
         on the name in the legend). Set to `null` if no specific model 
         concerned
      - `text`: list of character string, text to add below the plot. 
      - Set to `null` is no notes to add.
      
    For example:
    ```
    "scenario_plot": {
      "peak": {
        "PEAK NAME": {
          "start_date": "2020-01-01",
          "end_date": "2021-12-01",
          "target_specific": "inc hosp"
        }
      },
      "notes": {
        "models": ["UNCC-hierbin", "UTA-ImmunoSEIRS"],
        "text": ["* A correction to the UNCC-hierbin and UTA-ImmunoSEIRS projections was made on 2022-01-21 and 2022-01-24, respectively"]
      }
    }
     ```

- `scenario_comparison`:  
	- `reference`: dict, containing for each comparison:
	the comparison title (key) and the two scenarios to compare in a list 
	`[COMPARISON, REFERENCE]` (value)


- `multi-pathogen_plot`:  
  - `pathogen`: contains the pathogen(s) specific information. If more than
  one pathogen AND multi-pathogen in the list of plot: only the first pathogen
  will be included in the plot. ALL the pathogens included in the combined 
  multi-pathogen plot. 
  Each element should be named by the pathogen name (`pathogen_name`, lower case)
    - `display_name`: character string, name of the pathogen to display
    - `website`: character string, associated website address of the pathogen
    - `round`: character string, internal name of the round of the pathogen, used
    in the plot (should match a folder in the 
    `visualization/data-visualization/<pathogen_name>/` folder)
    - `scenario`: dict, containing the scenario id (`"id"`) and the associated
    name of each selected scenario (`"name"`) of the second pathogen. It should
    also contain a dictionary (`dict`) with the scenario id (as keys) and associated
    numeric as character string (in the website visualization files, as values)
    - `default_selection`: list, scenario id of one or multiple
    specific scenario id to use a default selection in the plot
    ```
    "covid-19": {
          "display_name": "COVID-19",
          "website": "https://covid19scenariomodelinghub.org/",
          "round": "round17",
          "scenario": {
            "id":["A-2023-04-16", "B-2023-04-16", "C-2023-04-16", "D-2023-04-16", "E-2023-04-16", "F-2023-04-16"],
            "name":["No booster, low immune escape", "No booster, high immune escape", "65+ booster, low immune escape",
              "65+ booster, high immune escape", "All booster, low immune escape", "All booster, high immune escape"],
            "dict": {"A-2023-04-16": "65", "B-2023-04-16": "66", "C-2023-04-16": "67", "D-2023-04-16":  "68",
              "E-2023-04-16":  "69", "F-2023-04-16": "70"}
          },
          "default_selection": ["D-2023-04-16"]
        }
     ```
  - `peak`:  
    - `"start_date"` and `"end_date"` and a peak name
      for one or multiple previous peaks defined by a specific time frame (if "end_date" 
      is null, ongoing time frame) and used to draw a horizontal red dotted line on the 
      scenario plot showing the maximum peak on this time frame. `null` is no peak 
      information on the plot.  
  - `unselect`: list of scenario ID to NOT select by default for RSV.  

### Round Example
```
{
 "Round 1": {
    "date_round": "2023-11-12",
    "show": "True",
    "plot_tab": ["scenario", "spaghetti", "model_specific", "scen_comparison", "peak_time_model", "peak_size",
      "multipat_plot_comb"],
    "target": {
      "inc hosp": "Incident Hospitalization",
      "cum hosp": "Cumulative Hospitalization"
    },
    "age_group": {
      "0-0.99": "Under 1 year old",
      "1-4": "1 to 4 years old (included)",
      "5-64": "5 to 64 years old (included)",
      "65-130": "65+ year old",
      "0-130": "Overall Population"
  },
    "def_target": "hosp",
    "models": ["Ensemble_LOP_untrimmed", "Ensemble_LOP", "Ensemble", "UT-ImmunoSEIRS", "NotreDame-FRED",
      "USC-SIkJalpha", "CU-RSV_SVIRS", "UVA-EpiHiperRSV", "NIH-RSV_WIN"],
    "point": {
      "type": "quantile",
      "type_id": 0.5
    },
    "ensemble": {
      "default": "Ensemble_LOP_untrimmed",
      "hide": ["Ensemble_LOP", "Ensemble"]
    },
    "zeroed_file": "Sample",
    "horizon_limit": {
      "required": 29,
      "optional": 29
    },
    "scenario_plot": {
      "peak": {
        "Peak Season 2022-2023": {
          "target_specific": "inc hosp",
          "start_date": "2022-08-01",
          "end_date": "2023-07-01"
        }
      },
      "notes": null
    },
    "scenario_comparison": {
      "reference": {
        "Optimistic Senior Protection &<br>Optimistic Infant Protection (A)": [
          "A-2023-10-27",
          "E-2023-10-27"
        ],
        "Pessimistic Senior Protection &<br>Optimistic Infant Protection (B)": [
          "B-2023-10-27",
          "E-2023-10-27"
        ],
        "Optimistic Senior Protection &<br>Pessimistic Infant Protection (C)": [
          "C-2023-10-27",
          "E-2023-10-27"
        ],
        "Pessimistic Senior Protection &<br>Pessimistic Infant Protection (D)": [
          "D-2023-10-27",
          "E-2023-10-27"
        ]
      }
    },
    "multi-pathogen_plot": {
      "pathogen": {
        "covid-19": {
          "display_name": "COVID-19",
          "website": "https://covid19scenariomodelinghub.org/",
          "round": "round17",
          "scenario": {
            "id":["A-2023-04-16", "B-2023-04-16", "C-2023-04-16", "D-2023-04-16", "E-2023-04-16", "F-2023-04-16"],
            "name":["No booster, low immune escape", "No booster, high immune escape", "65+ booster, low immune escape",
              "65+ booster, high immune escape", "All booster, low immune escape", "All booster, high immune escape"],
            "dict": {"A-2023-04-16": "65", "B-2023-04-16": "66", "C-2023-04-16": "67", "D-2023-04-16":  "68",
              "E-2023-04-16":  "69", "F-2023-04-16": "70"}
          },
          "default_selection": ["D-2023-04-16"]
        },
        "flu": {
          "website": "https://fluscenariomodelinghub.org/",
          "round": "round4",
          "round_display": "1 - 2023/2024",
          "display_name": "Flu",
          "scenario": {
            "id":["A-2023-08-14","B-2023-08-14","C-2023-08-14","D-2023-08-14","E-2023-08-14", "F-2023-08-14"],
            "name":["High vaccine coverage, A/H3N2 dominance",
              "High vaccine coverage, A/H1N1 dominance", "Business as usual vaccine coverage, A/H3N2 dominance",
              "Business as usual vaccine coverage, A/H1N1 dominance", "Low vaccine coverage, A/H3N2 dominance",
              "Low vaccine coverage, A/H1N1 dominance"],
            "dict": {"A-2023-08-14": "13", "B-2023-08-14": "14", "C-2023-08-14": "15", "D-2023-08-14":  "16",
              "E-2023-08-14":  "17", "F-2023-08-14": "18"}
          },
          "default_selection": ["C-2023-08-14","D-2023-08-14"]
        }
      },
      "peak": {
        "Peak Season 2022-2023": {
          "start_date": "2022-09-30",
          "end_date": "2023-07-01"
        }
      },
      "unselect": ["A-2023-10-27", "B-2023-10-27", "C-2023-10-27", "E-2023-10-27", "F-2023-10-27"]
    },
    "gold_standard": {
      "inc hosp": "rsvnet_hospitalization",
      "inc death": null,
      "cum hosp": null,
      "cum death": null
    },
    "multi": "True",
    "abstract": "False"
  },
 "Round 2": {...}
}
```

## Additional Information

All the scenario id and team-model name, number, and full name (display name)
information is accessible in the `sysdata.rda` files in the associated DATA 
repository of each pathogen. For access, contact @LucieContamin.

