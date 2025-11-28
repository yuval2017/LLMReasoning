import re
import pandas as pd
import os
import torch
from sympy import oo, zoo, Abs, Float
import numpy as np

# A helper: translate superscript digits to ascii digits
_SUPERSCRIPT_MAP = str.maketrans(
    {
        "⁰": "0",
        "¹": "1",
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
        "⁺": "+",
        "⁻": "-",
        "⁽": "(",
        "⁾": ")",
    }
)

# Regex that matches normalized numeric forms (after preprocessing)
_NORMAL_NUM_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def _normalize_string(s: str) -> str:
    s = s.strip()
    s = s.replace(" ", "")
    s = s.replace("E", "e")
    # Normalize Unicode minus/dash to ASCII hyphen-minus
    s = s.replace("–", "-").replace("−", "-").replace("—", "-")
    # Normalize multiplication sign variants to 'x'
    s = s.replace("×", "x").replace("⋅", "x").replace("·", "x")
    s = s.replace("X", "x")
    # Remove thousands separators (commas)
    s = s.replace(",", "")
    # Translate superscripts to normal digits/signs
    s = s.translate(_SUPERSCRIPT_MAP)
    # Convert common forms like '2.3x10^5' or '2.3x10 5' -> '2.3e5'
    s = re.sub(r"x\s*10\^?\s*\(?([+-]?\d+)\)?", r"e\1", s)
    # also handle cases where people wrote '10**5' -> 'e5' (optional)
    s = re.sub(r"x\s*10\*\*\s*([+-]?\d+)", r"e\1", s)
    return s


def load_all(folder_path: str, filter_len) -> pd.DataFrame:
    file_names = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    dfs = []
    for file_name in file_names:
        df = pd.read_csv(os.path.join(folder_path, file_name))
        if len(df) == filter_len:
            dfs.append((file_name, df))
            print(f"{file_name}:", len(df))
    return dfs


# new_row = {
#     "Expression": expr,
#     "Model Prompt": prompt,
#     "Full Model Response": answer,
#     "Added Operation/Function": op_or_func,
#     "Thought Process": think_part,
#     "Num of thought Tokens": num_thought_tokens,
#     "Model Answer": final_answer,
#     "Num of answer Tokens": num_answer_tokens,
#     "Model final Answer": final_model_value,
#     "Value": value,
#     "Time Taken (s)": f"{total_time:.4f}",
# }


def safe_abs_diff(a, b):
    # Handle None
    if a is None or b is None:
        return None

    # Handle infinities
    if a is oo and b is oo:
        return 0  # undefined (∞ - ∞)
    if a is -oo and b is -oo:
        return 0
    if (a in {oo, -oo}) or (b in {oo, -oo}):
        return oo  # ∞ - finite = ∞

    # Regular case
    return Abs(a - b)

def convert_to_sympy(s: str):
    try:
        value_decimal = Float(s)
        return value_decimal
    except (MemoryError):
        # If the string starts with a minus, use -∞; otherwise +∞
        if str(s).strip().startswith("-"):
            value_decimal = -oo
        else:
            value_decimal = oo
        print(
            f"Converted model value to Infinity due to overflow: {s}"
        )
        return value_decimal
    except Exception as e:
        print(f"⚠️ Exception type: {type(e).__name__}")
        print(f"⚠️ Exception message: {e}")
        raise e


def eval_row(row) -> pd.DataFrame:
    values = ["nan", float("nan"), np.nan, " NaN ", None, "NULL"]

    model_val_str = row["Model final Answer"]

    print("Original Model Value str:", model_val_str)
    print("original True Value str:", row["Value"])
    true_val_str = row["Value"]
    number_model_decimal = None
    value_decimal = None
    substraction = None
    if model_val_str in values:
        return "nan"
    try:
        # Map infinity
        if model_val_str in {"∞", "∞", "∞", "Infinity", float("inf")}:
            print("converted model value to Infinity")
            number_model_decimal = oo
        elif model_val_str in {"-∞", "−∞", "–∞", "-Infinity", float("-inf")}:
            number_model_decimal = -oo
        else:
            if type(model_val_str) is str:
                if "solution" in model_val_str.lower():
                    return "nan"
                model_val_str = _normalize_string(model_val_str)
                number_model_decimal = convert_to_sympy(model_val_str)
                value_decimal = convert_to_sympy(true_val_str)
     

        print("try to substract")
        substraction = safe_abs_diff(number_model_decimal, value_decimal)
        print(f"after substract: {substraction}")
        # print(f"Model Value str: {model_val_str}, Model Value: {number_model_decimal}, True Value: {value_decimal}, Abs Error: {substraction}")
        return substraction
    except Exception as e:
        print(f"Error converting to Decimal: {e}")
        print(
            f"Model Value str: {model_val_str}, Model Value: {number_model_decimal}, True Value: {value_decimal}, Abs Error: {substraction}"
        )
        raise e


if __name__ == "__main__":
    folder_path = "result/base_expressions"
    dfs = load_all(folder_path, filter_len=200)
    df_test = dfs[0][1]
    print(df_test.head())
    for name, df in dfs[8::]:
        print("Evaluating DF:", name)
        for index, row in df.iterrows():
            print(f"Row {index}:")
            try:
                eval_row(row)
            except Exception as e:
                print("Error DF name:", name)
                print(f"Error at row {index}: {e}")
                exit(0)
            finally:
                print(50 * "-")
    exit(0)
