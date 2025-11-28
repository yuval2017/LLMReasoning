import pandas as pd
import os
# read all files from folder
folder_path = "result/hard_expressions"

file_names = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
dfs = []
for file_name in file_names:
    df = pd.read_csv(os.path.join(folder_path, file_name))
    dfs.append((file_name, df))
    print(f"{file_name}:", len(df))
print(f"Number of files: {len(dfs)}")

exit(0)

pd_columns = [df_name for df_name, _ in dfs]
df_num_tokens = pd.DataFrame(columns=pd_columns)
column_name = "Num of thought Tokens"
#column_name = "Model Answer"
#column_name = "Model final Answer"
#columns_name = "Value"
rows = []
num_of_tokens_arrays = [df[column_name].tolist() for _, df in dfs]
max_length = max(len(arr) for arr in num_of_tokens_arrays)
for row_index in range(max_length):
    row_dict = {}
    for file_name,df in dfs:
        if len(df) > row_index:
            row_dict[file_name] = df[column_name].iloc[row_index]
        else:
            row_dict[file_name] = "N/A"
    rows.append(row_dict)
df_num_tokens = pd.DataFrame(rows)
# print it beautifully
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df_num_tokens)
