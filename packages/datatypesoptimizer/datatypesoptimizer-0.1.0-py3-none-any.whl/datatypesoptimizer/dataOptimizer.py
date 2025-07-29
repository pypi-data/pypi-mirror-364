import pandas as pd
import numpy as np

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimizes the data types of a Pandas DataFrame to reduce memory usage.

    This function attempts to downcast numeric columns (integers and floats)
    to the smallest possible data type without losing precision. It skips
    object (string), boolean, and categorical columns, as these typically
    don't benefit from the same downcasting logic or are already optimized.

    Args:
        df (pd.DataFrame): The input DataFrame to optimize.

    Returns:
        pd.DataFrame: The DataFrame with optimized data types.

    Raises:
        TypeError: If the input is not a Pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    df_optimized = df.copy()

    for col in df_optimized.columns:
        col_type = df_optimized[col].dtype

        # Optimize numeric types (integers and floats)
        if pd.api.types.is_numeric_dtype(col_type):
            if pd.api.types.is_integer_dtype(col_type):
                # Attempt to downcast to smallest integer type
                df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
            elif pd.api.types.is_float_dtype(col_type):
                # Attempt to downcast to smallest float type
                df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
        # Skip object (string), boolean, and categorical types
        elif pd.api.types.is_object_dtype(col_type) or \
             pd.api.types.is_categorical_dtype(col_type) or \
             pd.api.types.is_bool_dtype(col_type):
            continue
        # For other types like datetime, timedelta, etc., they are generally
        # left as is unless specific optimization for those types is required.
        else:
            pass

    return df_optimized
