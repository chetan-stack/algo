import pandas as pd
import pandas_ta as ta

# # Create a DataFrame so 'ta' can be used.
# df = pd.DataFrame()
#
# # Help about this, 'ta', extension
#
# # List of all indicators
# # df.ta.indicators()
#
# df = df.ta.cdl_pattern(name="all")
#
# print(df)

# Define a dictionary to map operator symbols to their corresponding operations
operator_map = {
    '=': lambda x, y: x == y,
    '>': lambda x, y: x > y,
    '<': lambda x, y: x < y,
    '>=': lambda x, y: x >= y,
    '<=': lambda x, y: x <= y
}

# Define variables
variable_name = 'x'
variable_value = 10

# Define the operator symbol you want to use
operator_symbol = '='

# Define the comparison value
comparison_value = 5

# Perform the comparison using the selected operator
result = operator_map[operator_symbol](variable_value, comparison_value)

# Use the result in an if condition
if result:
    print(f"{variable_name} {operator_symbol} {comparison_value}")
else:
    print(f"{variable_name} {operator_symbol} {comparison_value} is not True")

