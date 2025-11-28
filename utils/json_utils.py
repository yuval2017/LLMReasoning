import pandas as pd

def flat_json(json_data, filter_keys):
    flat_data = {}
    for key, value in json_data.items():
        if key not in filter_keys:
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_data[sub_key] = sub_value
            else:
                flat_data[key] = value
    for key in filter_keys:
        flat_data[key] = json_data[key]
    return flat_data
      
def expand_to_rows(data, 
                   column_name, 
                   new_column_name):
    rows = data[column_name]
    returned_rows = []
    #detete this column name
    del data[column_name]
    #flat object except result culumn
    for row in rows:
        data_copy = data.copy()
        data_copy[new_column_name] = row
        returned_rows.append(data_copy)
    return returned_rows
