import pandas as pd
import json
from utils import flat_json, expand_to_rows

# main entry

if __name__ == "__main__":
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
    #test flattening
    flat_test = flat_json(test_row, {"generate_data"})
    print("Flat test:", flat_test)

    #expand to rows test
    expanded_rows = expand_to_rows(flat_test, "generate_data", "result")

    
    for row in expanded_rows:
        print("Expanded row:", row)
        print("--" * 20)
    print("=====" * 20)


    expand_result = []
    
    #flat result again
    for row in expanded_rows:
        flat_row = flat_json(row, set())
        expand_result.append(flat_row)
        print("Flat expanded row:", flat_row)
        print("--" * 20)

    df = pd.DataFrame(expand_result)
    print("Final DataFrame:")
    print(df)
    print(df.info())