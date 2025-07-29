import data_explorer

df = data_explorer.get_import("SN", "2021", "2022")

print(df.head())
