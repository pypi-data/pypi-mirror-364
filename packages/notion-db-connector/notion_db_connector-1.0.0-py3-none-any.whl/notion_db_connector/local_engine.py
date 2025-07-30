# -*- coding: utf-8 -*-
"""
Executes SQL-like queries on a pandas DataFrame.
"""
import pandas as pd
from .exceptions import SQLTranslationError

def execute_local_query(df: pd.DataFrame, parsed_sql: dict) -> pd.DataFrame:
    """
    Executes a query with GROUP BY and aggregations on a pandas DataFrame.

    Args:
        df: The DataFrame to query.
        parsed_sql: A dictionary representing the parsed SQL query from sqlglot.

    Returns:
        A new DataFrame containing the results of the aggregation.
    """
    if df.empty:
        return pd.DataFrame()

    group_by_columns = parsed_sql.get("group_by")
    if not group_by_columns:
        raise SQLTranslationError("Local query execution requires a GROUP BY clause.")

    # Ensure all grouping columns exist in the DataFrame
    missing_cols = [col for col in group_by_columns if col not in df.columns]
    if missing_cols:
        raise SQLTranslationError(f"Grouping columns not found in database: {', '.join(missing_cols)}")

    grouped = df.groupby(group_by_columns)
    
    agg_expressions = {}
    select_expressions = parsed_sql.get("properties", [])

    for expr in select_expressions:
        if isinstance(expr, dict) and 'aggregate' in expr:
            func = expr['aggregate']['func'].upper()
            col = expr['aggregate']['col']
            alias = expr.get('alias', f"{col}_{func.lower()}")

            if col != '*' and col not in df.columns:
                 raise SQLTranslationError(f"Column '{col}' for aggregation not found in database.")

            if func == 'COUNT':
                if col == '*':
                    agg_expressions[alias] = ('id', 'count') # Use a guaranteed column like 'id'
                else:
                    agg_expressions[alias] = (col, 'count')
            elif func == 'SUM':
                agg_expressions[alias] = (col, 'sum')
            elif func == 'AVG':
                agg_expressions[alias] = (col, 'mean')
            elif func == 'MIN':
                agg_expressions[alias] = (col, 'min')
            elif func == 'MAX':
                agg_expressions[alias] = (col, 'max')
            else:
                raise SQLTranslationError(f"Unsupported aggregate function: {func}")

    if not agg_expressions:
        raise SQLTranslationError("No aggregate functions found in SELECT clause for local query.")

    # Perform the aggregation
    # The dictionary unpacking is for pandas >= 0.25
    result_df = grouped.agg(**agg_expressions).reset_index()

    # Rename columns to match aliases
    final_columns = group_by_columns + list(agg_expressions.keys())
    
    # The result_df should already have the correct alias names.
    # We just need to select the final columns in the right order.
    
    # The properties in parsed_sql might just be the column names for group by
    # or the aggregation dicts. We need to construct the final list of selected columns.
    final_select_order = []
    for expr in select_expressions:
        if isinstance(expr, str): # A group by column
            final_select_order.append(expr)
        elif isinstance(expr, dict) and 'aggregate' in expr:
            alias = expr.get('alias', f"{expr['aggregate']['col']}_{expr['aggregate']['func'].lower()}")
            final_select_order.append(alias)

    return result_df[final_select_order]
def execute_local_join(left_df: pd.DataFrame, right_df: pd.DataFrame, join_info: dict) -> pd.DataFrame:
    """
    Executes a JOIN operation on two pandas DataFrames.

    Args:
        left_df: The left DataFrame for the join.
        right_df: The right DataFrame for the join.
        join_info: A dictionary containing join parameters from the translator.

    Returns:
        A new DataFrame containing the result of the join.
    """
    join_type = join_info.get("join_type", "inner")
    left_on = join_info.get("left_on")
    right_on = join_info.get("right_on")

    if not all([left_on, right_on]):
        raise SQLTranslationError("JOIN requires ON condition with left and right columns specified.")

    # Map SQL JOIN types to pandas 'how' parameter
    how_map = {
        "inner": "inner",
        "left": "left",
        "left outer": "left",
        "right": "right",
        "right outer": "right",
        "full outer": "outer",
    }
    how = how_map.get(join_type)
    if not how:
        raise SQLTranslationError(f"Unsupported JOIN type: {join_type}")

    if left_on not in left_df.columns:
        raise SQLTranslationError(f"Join key '{left_on}' not found in the left table.")
    if right_on not in right_df.columns:
        raise SQLTranslationError(f"Join key '{right_on}' not found in the right table.")

    # Perform the merge
    merged_df = pd.merge(
        left_df,
        right_df,
        left_on=left_on,
        right_on=right_on,
        how=how,
        suffixes=('_left', '_right') # Add suffixes to handle overlapping column names
    )

    return merged_df