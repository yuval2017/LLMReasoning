import pandas as pd
import json
from utils import flat_json
# main entry
def append_col_horizontally(flat_data, col_name, prefix):
    """
    - generate_data flattened horizontally with RES1_, RES2_, ...
    """
    

    # Flatten generate_data horizontally
    for i, entry in enumerate(flat_data.pop(col_name, []), start=1):
        for key, value in entry.items():
            flat_data[f"{prefix}{i}_{key}"] = value

    # Return as a single-row DataFrame
    return flat_data

def take_all_key_with_prefix(data, suffix:str):
    result = []
    for key, value in data.items():
        if key.endswith(suffix):
            result.append(value)
    return result

if __name__ == "__main__":
    prefix = "RES"
    suffix = "num_of_think_tokens"
    path = "result/deepseek_r1_distill_qwen_7b/asdiv_evaluation_format.json"
    with open(path, "r") as f:
        data = json.load(f)
    rows_sorted = sorted(data, key=lambda x: int(x["metadata"]["grade"]))
    col_name = "generate_data"


    all_rows = []
    for i, test_row in enumerate(rows_sorted[:1]):
        flat_data = flat_json(test_row, filter_keys={col_name})
        row = append_col_horizontally(flat_data, col_name, prefix=prefix)
        print("Flattened single row DataFrame:")
       
        arr_data = take_all_key_with_prefix(row, suffix)
        print(arr_data)
        mean_value = sum(arr_data) / len(arr_data)
        min_value = min(arr_data)
        max_value = max(arr_data)

        row[f"mean_value_{suffix}"] = mean_value
        row[f"min_value_{suffix}"] = min_value
        row[f"max_value_{suffix}"] = max_value

        for key, value in row.items():
            print(f"{key}: {value}")

        all_rows.append(row)
    df = pd.DataFrame(all_rows)

    #print(df.info())


            

    json_path = "result/asdiv_phi4_plus_results.json"
    test_row = {
        "dataset": "asdiv",
        "split": "full",
        "question_id": "nluds-0001",
        "question": "junk",
        "answer": "9",
        "has_reasoning": False,
        "reasoning": "null",
        "metadata": {
            "grade": "1",
            "solution_type": "Addition",
            "formula": "7+2=9",
            "source": "http://www.k5learning.com",
            "subtypes": []
        },
        "generate_data": [
            {
                "think":"123",
                "final_answer": "null",
                "num_of_think_tokens": 32522,
                "num_of_answer_tokens": "N/A",
                "generation_time": 2415.945231800899
            },
            {
                "think":"1234",
                "final_answer": "null",
                "num_of_think_tokens": 732,
                "num_of_answer_tokens": 40,
                "generation_time": 50.27416557073593
            },
            {
                "think":"12345",
                "final_answer": "null",
                "num_of_think_tokens": 601,
                "num_of_answer_tokens": 42,
                "generation_time": 40.873942798003554
            },
            {
                "think":"12356",
                "final_answer": "null",
                "num_of_think_tokens": 293,
                "num_of_answer_tokens": 26,
                "generation_time": 20.23920996952802
            },
            {
                "think":"1234567",
                "final_answer": "null",
                "num_of_think_tokens": 399,
                "num_of_answer_tokens": 29,
                "generation_time": 27.26210433896631
            }
        ]
    }
    #print(row.info())
    #expand to rows test
    # expanded_rows = expand_to_rows(flat_test, "generate_data", "result")

    
    # for row in expanded_rows:
    #     print("Expanded row:", row)
    #     print("--" * 20)
    # print("=====" * 20)


    # expand_result = []
    
    # #flat result again
    # for row in expanded_rows:
    #     flat_row = flat_json(row, set())
    #     expand_result.append(flat_row)
    #     print("Flat expanded row:", flat_row)
    #     print("--" * 20)

    # df = pd.DataFrame(expand_result)
    # print("Final DataFrame:")
    # print(df)
    # print(df.info())