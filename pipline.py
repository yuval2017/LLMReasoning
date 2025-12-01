# load base task
# target
# count tokens
# size of each tokens parts
# time
# arithmetic operations always use the same model
# Example usage
import re
from config import init_config

# init configurations
config = init_config()
config.init_env()
# config.clear_processes()

from utils import load_model, generate, extract_think_and_after
from models_factory import get_default_system_prompt, get_model_and_split_function
from state import state
import torch
import json
from add_operation import ExpressionGenerator
from functools import wraps
import time
import os
import pandas as pd


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        total_time = end - start
        # print(f"{func.__name__} took {end - start:.4f} seconds")
        return result, total_time

    return wrapper


@timed
def generate2(messages):
    answer = generate(model, tokenizer, messages)
    return answer


def num_of_tokens(text):
    return len(tokenizer.tokenize(text, add_special_tokens=False))


def debug_row(d: dict):
    for k, v in d.items():
        print(f"{k}: {v}")
        print("^" * 20)
    print("-" * 50)


def extract_final_answer(answer: str):
    prompt = f"This is the model's response:\n{answer}\n Please extract and return **only the final numerical answer**. If there is no clear numerical answer, return 'N/A'."
    messages = [
        {"role": "system", "content": general_sys_prompt},
        {"role": "user", "content": prompt},
    ]
    answer, _ = generate2(messages)
    think_part, final_answer = split_function(answer)
    return final_answer


csv_columns = [
    "Expression",
    "Full Model Response",
    "Model Prompt",
    "Added Operation/Function",
    "Thought Process",
    "Num of thought Tokens",
    "Model Answer",
    "Num of answer Tokens",
    "Model final Answer",
    "Value",
    "Time Taken (s)",
]


def my_generate(expression_data, iterations: int = 5):
    expr = expression_data["SYMPY expression"]
    op_or_func = expression_data["New op"]
    value = expression_data["Value"]
    expr_for_llm = expression_data["Expression for LLM"]

    prompt = f"Solve the following expression: {expr_for_llm}\nReturn only the numerical answer rounded to 4 decimal places."
    messages = [
        {"role": "system", "content": general_sys_prompt},
        {"role": "user", "content": prompt},
    ]
    new_data = []
    for _ in range(iterations):
        answer, total_time = generate2(messages)
        think_part, final_answer = split_function(answer)
        num_thought_tokens = max_tokens
        num_answer_tokens = 0

        if final_answer is not None:
            final_model_value = extract_final_answer(final_answer)
            num_answer_tokens = num_of_tokens(final_answer)
            num_thought_tokens = num_of_tokens(think_part)
        else:
            final_model_value = "N/A"
            final_answer = "N/A"

        new_row = {
            "Expression": expr,
            "Model Prompt": prompt,
            "Full Model Response": answer,
            "Added Operation/Function": op_or_func,
            "Thought Process": think_part,
            "Num of thought Tokens": num_thought_tokens,
            "Model Answer": final_answer,
            "Num of answer Tokens": num_answer_tokens,
            "Model final Answer": final_model_value,
            "Value": value,
            "Time Taken (s)": f"{total_time:.4f}",
        }

        # sanity check
        missing_cols = set(csv_columns) - set(new_row.keys())
        extra_cols = set(new_row.keys()) - set(csv_columns)
        print("MISSING:", missing_cols, "EXTRA:", extra_cols)
        assert len(missing_cols) == 0 and len(extra_cols) == 0, (
            "Column mismatch in new_row"
        )
        # debug
        debug_row(new_row)

        new_data.append(new_row)

        # Clear GPU cache to manage memory
        torch.cuda.empty_cache()
    return new_data


def get_last_row_as_dict(df: pd.DataFrame):
    if df.empty:
        return None
    last_row = df.iloc[-1]
    return last_row.to_dict()


def process_expressions(path: str, result_path: str, iterations: int = 3):
    """
    Processes expressions from a CSV at `path`, generates results, and saves to `result_path`.
    """
    from_row = 0

    if os.path.exists(result_path):
        result_df = pd.read_csv(result_path)
        from_row = len(result_df)
        if from_row % iterations != 0:
            raise ValueError(
                f"Result CSV at {result_path} seems corrupted. Number of rows ({from_row}) is not a multiple of iterations ({iterations})."
            )
        # Determine the starting row for the next batch
        from_row = from_row // iterations
        print(f"Resuming from row {from_row} in {path}")
        expressions_df = pd.read_csv(path)
        if from_row >= len(expressions_df):
            print(f"All expressions in {path} have already been processed.")
            return

        last_row = get_last_row_as_dict(result_df)
        if last_row:
            print("Resuming from last row num:")
            # get next row to process
            value_next_row = expressions_df.iloc[from_row].to_dict()
            print(
                f"Last expression evaluated: {last_row['Expression']}\nNext expression to evaluate: {value_next_row['SYMPY expression']}"
            )
        else:
            raise ValueError("Result CSV exists but is empty. Please check the file.")

    else:
        result_df = pd.DataFrame(columns=csv_columns)
        expressions_df = pd.read_csv(path)

    if from_row > len(expressions_df):
        print(f"All expressions in {path} have already been processed.")
        return
    for i in range(from_row, len(expressions_df)):
        row_data = expressions_df.iloc[i].to_dict()
        add_rows = my_generate(row_data, iterations=iterations)
        # Save after each expression to avoid data loss
        add_df = pd.DataFrame(add_rows, columns=csv_columns)
        if not add_df.empty:
            result_df = pd.concat([result_df, add_df], ignore_index=True)
            result_df.to_csv(result_path, index=False, encoding="utf-8-sig")


import sys
import re
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python dummy.py <gpu_id> <task>")
        sys.exit(1)
    print("Starting process...")
    gpu_id = int(sys.argv[1])
    expressions = [expr.strip() for expr in re.findall(r'\([^()]*\)', sys.argv[2])]

    for i, expr in enumerate(expressions):
        print(f"Expression {i + 1}: {expr}")
        # Process each expression

    print(f"Worker (PID: {os.getpid()}) on GPU {gpu_id}")
    # load models from data folder
    with open("data/models.json", "r") as f:
        models = json.load(f)
    model_key = "microsoft_phi-4_Plus"
    model_name, split_function = get_model_and_split_function(model_key)
    general_sys_prompt = get_default_system_prompt(model_name)
    model_kwargs = {
        "dtype": torch.float16,
        "trust_remote_code": True,
        "use_cache": False,
    }
    tokenizer_kwargs = {}
    kwargs = {"model_kwargs": model_kwargs, "tokenizer_kwargs": tokenizer_kwargs}
    model, tokenizer = load_model(model_name, device_map=f"cuda:{gpu_id}", **kwargs)
    # Check the device of the model parameters
    device = next(model.parameters()).device
    print("Model device:", device)

    print(model.config)
    max_tokens = model.config.max_position_embeddings
    print("Max tokens:", max_tokens)

    for expression in expressions:
        path = (
            f"data/hard_expressions/Expression_{expression.replace('/', '_div_')}.csv"
        )
        result_path = f"result/hard_expressions/arithmetic_expressions_{expression.replace('/', '_div_')}.csv"

        # path2 =  (
        #     f"data/base_expressions/Expression_{expression.replace('/', '_div_')}.csv"
        # )
        # result_path2 = f"result/base_expressions/arithmetic_expressions_{expression.replace('/', '_div_')}.csv"

        print(f"Processing expression: {expression}")
        print(f"Processing {path} -> {result_path}")

        process_expressions(path, result_path, iterations=5)