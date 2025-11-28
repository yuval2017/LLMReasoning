import pandas as pd
import torch

def validate_repeated_blocks(df: pd.DataFrame, column: str, k: int) -> bool:
    """
    Validate that the values in `column` repeat exactly k times consecutively
    and that the sequence of unique values is ordered (no repeats later).
    
    Args:
        df (pd.DataFrame): The DataFrame to validate.
        column (str): The column name to check.
        k (int): The required repeat count.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    values = df[column].to_numpy()
    
    # Check length divisibility
    if len(values) % k != 0:
        return False
    
    seen = []
    
    # Go block by block
    for i in range(0, len(values), k):
        group = values[i:i+k]
        
        # Rule 1: all values in group are the same
        if not all(v == group[0] for v in group):
            return False
        
        val = group[0]
        
        # Rule 2: no value repeats after its block
        if val in seen:
            return False
        seen.append(val)
    
    return True

def group_by_repeated_blocks(df: pd.DataFrame, 
                            k: int, 
                            group_col: str,
                            agg_funcs: dict) -> pd.DataFrame:
    """
    Group a DataFrame by repeated block column (no validation).
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        group_col (str): Column with repeated block values.
        k (int): Block size.
        agg_funcs (dict): Aggregations, e.g. {"val": np.mean, "score": max}.
    
    Returns:
        pd.DataFrame: Aggregated DataFrame (one row per block).
    """
    df = df.copy()
    df["_block"] = df.index // k
    
    grouped = (
        df.groupby([group_col, "_block"], sort=False)
          .agg(agg_funcs)
          .reset_index()
          .drop(columns="_block")   # keep group_col, drop only helper
    )
    
    return grouped

import pandas as pd

def merge_named_columns(dfs_with_names, columns):
    """
    Given a list of (name, df) tuples and a list of column names,
    create new columns with format 'dfname_colname' and append all into one DataFrame.

    Args:
        dfs_with_names (list): List of tuples (name: str, df: pd.DataFrame)
        columns (list): List of columns to select from each df

    Returns:
        pd.DataFrame: Concatenated DataFrame with renamed columns
    """
    new_cols = []
    
    for name, df in dfs_with_names:
        for col in columns:
            if col in df.columns:
                new_col_name = f"{name}_{col}"
                new_cols.append(df[col].rename(new_col_name))
    
    # Concatenate all columns side by side
    result = pd.concat(new_cols, axis=1)
    return result


def csv_to_tensor(df: pd.DataFrame) -> torch.Tensor:
    """
    Load a CSV file and convert its numeric contents into a PyTorch tensor (matrix).
    Column names are ignored.
    
    Args:
        csv_path (str): Path to the CSV file.
    
    Returns:
        torch.Tensor: 2D tensor with CSV values.
    """
    return torch.tensor(df.values, dtype=torch.float32)

