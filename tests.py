from unittest import result
import pandas as pd
import torch
#test utils
from utils import validate_repeated_blocks, group_by_repeated_blocks, merge_named_columns, csv_to_tensor
def test_validate_repeated_blocks():
    df1 = pd.DataFrame({"col": ["a","a","a","b","b","b","c","c","c"]})
    df2 = pd.DataFrame({"col": ["a","a","b","a","b","b","c","c","c"]})
    df3 = pd.DataFrame({"col": ["a","a","a","b","b","b","a","a","a"]})

    assert validate_repeated_blocks(df1, "col", 3) == True
    assert validate_repeated_blocks(df2, "col", 3) == False
    assert validate_repeated_blocks(df3, "col", 3) == False

test_validate_repeated_blocks()

def test_group_by_repeated_blocks():
    def value_range(series: pd.Series):
        return max(series) - min(series)
    df = pd.DataFrame({
        "col": ["a","a","a","b","b","b","c","c","c"],
        "val": [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0],
        "score": [10,20,30,40,50,60,70,80,90],
        "extra": [2,4,8,1,3,9,5,7,11]  # new column
    })


    result = group_by_repeated_blocks(
        df, 
        3,
        "col", 
        agg_funcs = {
            "val": "mean",          # NumPy mean works fine
            "score": "max",           # **string** for built-in max (avoids warning)
            "extra": value_range      # your custom function
        }
    )
    expected = pd.DataFrame({
        "col": ["a", "b", "c"],
        "val": [2.0, 5.0, 8.0],
        "score": [30, 60, 90],
        "extra": [6, 8, 6]  # expected aggregation for new column
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

test_group_by_repeated_blocks()


def test_merge_named_columns():
    df1 = pd.DataFrame({"a": [1,2,3], "b": [4,5,6]})
    df2 = pd.DataFrame({"a": [7,8,9], "b": [10,11,12]})

    result = merge_named_columns(
        [("df1", df1), ("df2", df2)],
        columns=["a", "b"]
    )
    expected = pd.DataFrame({
        "df1_a": [1,2,3],
        "df1_b": [4,5,6],
        "df2_a": [7,8,9],
        "df2_b": [10,11,12]
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
test_merge_named_columns()

def test_csv_to_tensor():
    df = pd.DataFrame({
        "col1": [1.0, 2.0, 3.0],
        "col2": [4.0, 5.0, 6.0]
    })
    tensor = csv_to_tensor(df, ["col1", "col2"])
    expected = torch.tensor([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])
    assert torch.equal(tensor, expected), f"Expected {expected}, got {tensor}"


print("All utils tests passed!")

#first formula

x = torch.tensor([
    [1, 4, 7, 10],
    [2, 5, 8, 11],
    [3, 6, 9, 12]
], dtype=torch.float32)

row_mean = x.mean(dim=1)           # [5.5, 6.5, 7.5]
diffs = row_mean[1:] - row_mean[:-1]  # [6.5-5.5, 7.5-6.5]


#second formula

x = torch.tensor([
    [1, 4, 7, 10],
    [2, 5, 8, 11],
    [3, 6, 9, 12]
], dtype=torch.float32)

# Step 1: row differences (keep dim in 2D)
row_diffs = x[1:] - x[:-1]   # shape (2,4)

# Step 2: mean across columns
row_means = row_diffs.mean(dim=1, keepdim=True)

print("Row differences:\n", row_diffs)
print("Row means:\n", row_means)