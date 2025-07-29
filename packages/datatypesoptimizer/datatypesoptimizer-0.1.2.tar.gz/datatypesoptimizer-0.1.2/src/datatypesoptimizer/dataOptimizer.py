import pandas as pd
import numpy as np

def optimize_dtypes(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    if verbose:
        start_mem = df.memory_usage(deep=True).sum() / (1024**2)
        print(f"Memory usage before optimization: {start_mem:.2f} MB")

    df_optimized = df.copy()

    for col in df_optimized.columns:
        col_type = df_optimized[col].dtype

        if pd.api.types.is_integer_dtype(col_type):
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
        elif pd.api.types.is_float_dtype(col_type):
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
        elif pd.api.types.is_object_dtype(col_type):
            try:
                temp_series = pd.to_datetime(df_optimized[col], errors='coerce')
                if not temp_series.isnull().all():
                    if temp_series.count() / len(temp_series) > 0.8:
                         df_optimized[col] = temp_series
                         continue
            except Exception:
                pass

            num_unique_values = df_optimized[col].nunique()
            num_total_values = len(df_optimized[col])
            if num_unique_values / num_total_values < 0.5 and num_total_values > 50:
                 df_optimized[col] = df_optimized[col].astype('category')
        elif pd.api.types.is_categorical_dtype(col_type) or \
             pd.api.types.is_bool_dtype(col_type):
            continue
        else:
            pass

    if verbose:
        end_mem = df_optimized.memory_usage(deep=True).sum() / (1024**2)
        print(f"Memory usage after optimization: {end_mem:.2f} MB")
        print(f"Memory reduced by: {(start_mem - end_mem):.2f} MB ({((start_mem - end_mem) / start_mem * 100):.2f}%)")

    return df_optimized
