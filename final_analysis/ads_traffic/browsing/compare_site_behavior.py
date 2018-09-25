import pandas as pd

def calc_diff (row):
    res = row['Ads-Percentage_cumulated'] - row['Ads-Percentage_stateless']
    return res

homepage_dataset = pd.read_csv("tables/cumulated_top_sites_0_P.csv",sep='\t')
cumulated_dataset = pd.read_csv("tables/cumulated_top_sites_4_P.csv", sep='\t')

merged_dataset = homepage_dataset.merge(cumulated_dataset, left_on="Site", right_on="Site", how="inner", suffixes=("_stateless", "_cumulated"))

# Rows with no NaNs are in both tables
in_both = merged_dataset.dropna(subset=["Site", "Site"])

# Select columns i want
selected_columns = in_both[['Site','Ads-Percentage_stateless', 'Ads-Percentage_cumulated']]

# create an unattached column with an index
selected_columns['result'] = selected_columns.apply(lambda row: calc_diff (row), axis=1)

result = selected_columns.sort_values(by=['result'], ascending=False)

result.to_csv('tables/sites_changed.csv', sep='\t', encoding='utf-8', index=False)
