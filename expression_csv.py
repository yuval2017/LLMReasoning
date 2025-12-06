from add_operation import ExpressionGenerator
import pandas as pd
import os

def print_base_expressions_csv_lengths():
    base_path = "data/base_expressions"
    csv_files = [f for f in os.listdir(base_path) if f.endswith(".csv")]
    for csv_file in csv_files:
        file_path = os.path.join(base_path, csv_file)
        df = pd.read_csv(file_path)
        print(df["SYMPY expression"].head(5))
        print(f"{csv_file}: {len(df)} rows")
#print_base_expressions_csv_lengths()

if not os.path.exists("data"):
    os.makedirs("data")
naive_ops = ["*", "/", "sqrt", "exp", "log", "pow"]
path1 = "data/with_range/base_expressions"
if not os.path.exists(path1):
    os.makedirs(path1)
rads_simple = ["sin", "cos", "tan"]
path2 = "data/with_range/hard_expressions"
if not os.path.exists(path2):
    os.makedirs(path2)
path3 = "data/with_range/very_hard_expressions"
if not os.path.exists(path3):
    os.makedirs(path3)
columns = ["New op", "SYMPY expression", "Expression for LLM", "Value"]
all_experiaments = [
    (naive_ops, path1),
    (naive_ops + rads_simple, path2),
    (None, path3)
]

starting_expressions_part1 = [
    "(3 + 5)",
    "(7 - 2)",
    "(4 * 6)",
    "(8 / 2)",
    "(1 + 2)"
]

starting_expressions_part2 = [
    "(5 * 3)",
    "(10 - 4)",
    "(6 / 3)",
    "(2 + 2)",
    "(9 - 3)"
]

starting_expressions_part3 = [
    "(8 / 4)",
    "(5 + 4)",
    "(3 * 7)", 
    "(12 / 4)", 
    "(6 + 2)"
]

starting_expressions_part4 = [
    "(8 * 2)",
    "(2 + 3)",
   "(4 + 6)",
    "(9 * 1)",
    "(7 + 3)"
]

def execute_to_csv(exp: str, path: str, filter_ops: list, num_steps: int = 30):
    expression = exp
    operation = "N/A"
    if os.path.exists(path):
        #take last expression
        df = pd.read_csv(path)
        if len(df) >= num_steps:
            print(f"File {path} already has {num_steps} or more steps. Skipping generation.")
            return
        #get last expression
        last_expr = df["SYMPY expression"].iloc[-1]
        print(f"Resuming from last expression:\n{last_expr}")
        gen = ExpressionGenerator(last_expr, filter_ops=filter_ops, valid_range = (-500, 500))
        gen.expr_demo_str = df["Expression for LLM"].iloc[-1]
        operation = df["New op"].iloc[-1]
        print(gen.sym_expr.evalf())
        # take next one
        expression, operation = next(gen)  # Advance once to sync state
    else:
        df = pd.DataFrame(columns=columns)
    
    gen = ExpressionGenerator(expression, filter_ops=filter_ops, valid_range = (-500, 500))
    #print(f"Starting expression:\n{gen.expr_str}")
    for _ in range(len(df), num_steps):
        new_row = {
            "New op": operation,
            "SYMPY expression": gen.expr_str,
            "Expression for LLM": gen.expr_demo_str,
            "Value": gen.sym_expr.evalf()
        }
        for key in new_row:
            print(f"{key}: {new_row[key]}")
        print("-----" * 10)
        _, operation = next(gen)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Saved to {path}")
        


num_of_rows = 40

def run_execute(expr, path_with_expr, ops):
    # wrapped function so it can run in a subprocess
    execute_to_csv(expr, path_with_expr, ops, num_steps=num_of_rows)

from multiprocessing import Process

def run_with_retry(expr, path_with_expr, ops, timeout=300):
    while True:
        p = Process(target=run_execute, args=(expr, path_with_expr, ops))
        p.start()
        p.join(timeout)
        if p.is_alive():
            print(f"Timeout reached. Killing process for {path_with_expr}")
            p.terminate()
            p.join()
            print(f"Retrying {path_with_expr}...")
        elif p.exitcode != 0:
            print(f"Process crashed for {path_with_expr} (exit code {p.exitcode}). Retrying...")
        else:
            print(f"Successfully created {path_with_expr} with starting expression {expr}")
            break


if __name__ == "__main__":
    all_starting_expressions = (
        starting_expressions_part1 +
        starting_expressions_part2 +
        starting_expressions_part3 +
        starting_expressions_part4
    )

    for ops, path in all_experiaments:
        is_failed = False
        for expr in all_starting_expressions:
            expr_path_name = expr.replace("/", "_div_")
            path_with_expr = os.path.join(path, f"Expression_{expr_path_name}.csv")

            # <- replace the old ProcessPoolExecutor block with this:
            run_with_retry(expr, path_with_expr, ops, timeout=600)

    print("All done")
