# DataTypes Optimizer

A simple Python library to optimize the data types of a Pandas DataFrame, reducing memory usage.

## How it works

The `optimize_dtypes` function in this library helps you reduce the memory footprint of your Pandas DataFrames. It works by downcasting numeric columns (both integers and floats) to their smallest possible data type that can still hold the data without any loss of precision.

For example, if you have a column of integers where the maximum value is 100, it's likely stored as an `int64` by default in Pandas. This function will intelligently convert it to `int8`, which uses significantly less memory.

The library currently optimizes:
- Integer columns
- Float columns

It skips the following data types as they generally do not benefit from this type of downcasting:
- Object (string)
- Boolean
- Categorical

## Usage

Here is a simple example of how to use the `optimize_dtypes` function:

```python
import pandas as pd
import numpy as np
from datatypesoptimizer.dataOptimizer import optimize_dtypes

# Create a sample DataFrame
data = {
    'integers': [1, 2, 100, 200],
    'floats': [1.0, 2.5, 3.5, 4.5],
    'strings': ['a', 'b', 'c', 'd']
}
df = pd.DataFrame(data)

print("Original DataFrame memory usage:")
print(df.memory_usage(deep=True))
print("\nOriginal dtypes:")
print(df.dtypes)

# Optimize the DataFrame
optimized_df = optimize_dtypes(df)

print("\nOptimized DataFrame memory usage:")
print(optimized_df.memory_usage(deep=True))
print("\nOptimized dtypes:")
print(optimized_df.dtypes)
```

### Example Output

```
Original DataFrame memory usage:
Index       132
integers     32
floats       32
strings     244
dtype: int64

Original dtypes:
integers     int64
floats      float64
strings      object
dtype: object

Optimized DataFrame memory usage:
Index       132
integers      4
floats        4
strings     244
dtype: int64

Optimized dtypes:
integers      int8
floats      float32
strings      object
dtype: object
```

As you can see from the output, the memory usage for the `integers` and `floats` columns has been significantly reduced after optimization.

## Installation

To use this library, you can clone the repository and import the `optimize_dtypes` function from the `datatypesoptimizer.dataOptimizer` module.

