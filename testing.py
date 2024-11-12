from main import *
import pandas as pd
import csv
import matplotlib.pyplot as plt


# time_dict_list = []
# for i in range(1):
#
#     fig, time_dict = spaghetti_plot(location='US', target='inc hosp', scenario=[1, 2, 3, 4, 5],
#                                  age_group="0-130", n_sample=100, med_plot=False, round_tab="Round 1")
#     time_dict_list.append(time_dict)
#
# df = pd.DataFrame(time_dict_list)
#
# mean = df.mean().to_frame()
#
# to_include = ['prep_dict', 'prep_subplots', 'scenario_1', 'scenario_2', 'scenario_3', 'scenario_4', 'scenario_5', 'total_time']
# filtered = mean.loc[to_include, :].rename(columns={0: 'val'})
#
# plot = filtered.plot.pie(y='val', labels=list(filtered.index), autopct='%1.1f%%')
# plt.legend(bbox_to_anchor=(1.05, 1))
# fig.show()


# total_times = []
# for i in range(100):
#     fig, total_time = spaghetti_plot(location='US', target='inc hosp', scenario=[1, 2, 3, 4, 5],
#                                age_group="0-130", n_sample=100, med_plot=False, round_tab="Round 1")
#     total_times.append(total_time)
#
# print(sum(total_times) / len(total_times))

# fig = spaghetti_plot(location='US', target='inc hosp', scenario=[1, 2, 3, 4, 5],
#                                 age_group="0-130", n_sample=100, med_plot=False, round_tab="Round 1")
#
# fig.show()
# draw_multi_pathogen_comb_plot('US', 'inc hosp', ['1'],  {"covid-19": ['D-2023-04-16', 'F-2023-04-16'], "flu": ['D-2023-08-14']}, 'Round 1', 'RSV')
fig = multipat_comb_plot(['1'], 'US', 'inc hosp', 'Round 1', ['D-2023-04-16', 'F-2023-04-16'], ['D-2023-08-14'], 'RSV')

fig.show()




