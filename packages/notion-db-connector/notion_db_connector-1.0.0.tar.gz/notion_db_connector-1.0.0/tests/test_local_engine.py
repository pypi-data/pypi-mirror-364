# -*- coding: utf-8 -*-
"""Unit tests for the local query engine."""
import pandas as pd
import pytest
from notion_db_connector.local_engine import execute_local_query
from notion_db_connector.exceptions import SQLTranslationError

@pytest.fixture
def sample_dataframe():
    """Provides a sample DataFrame for testing."""
    data = {
        'id': [f'id_{i}' for i in range(10)],
        'Category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'A', 'B', 'C'],
        'Value': [10, 20, 15, 30, 25, 12, 35, 18, 22, 33],
        'Region': ['North', 'South', 'North', 'South', 'North', 'South', 'North', 'South', 'North', 'South']
    }
    return pd.DataFrame(data)

def test_simple_group_by_count(sample_dataframe):
    """Tests a simple GROUP BY with COUNT(*)."""
    parsed_sql = {
        "properties": [
            "Category",
            {"aggregate": {"func": "COUNT", "col": "*"}, "alias": "count_all"}
        ],
        "group_by": ["Category"]
    }
    result = execute_local_query(sample_dataframe, parsed_sql)
    
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ['Category', 'count_all']
    assert len(result) == 3
    
    # Check values
    result = result.sort_values(by='Category').reset_index(drop=True)
    assert result.loc[0, 'Category'] == 'A'
    assert result.loc[0, 'count_all'] == 4
    assert result.loc[1, 'Category'] == 'B'
    assert result.loc[1, 'count_all'] == 3
    assert result.loc[2, 'Category'] == 'C'
    assert result.loc[2, 'count_all'] == 3

def test_group_by_multiple_aggregates(sample_dataframe):
    """Tests GROUP BY with multiple aggregate functions (SUM, AVG)."""
    parsed_sql = {
        "properties": [
            "Category",
            {"aggregate": {"func": "SUM", "col": "Value"}, "alias": "total_value"},
            {"aggregate": {"func": "AVG", "col": "Value"}, "alias": "avg_value"}
        ],
        "group_by": ["Category"]
    }
    result = execute_local_query(sample_dataframe, parsed_sql)
    
    assert list(result.columns) == ['Category', 'total_value', 'avg_value']
    result = result.sort_values(by='Category').reset_index(drop=True)
    
    # Category A: 10, 15, 12, 18 -> Sum: 55, Avg: 13.75
    assert result.loc[0, 'total_value'] == 55
    assert result.loc[0, 'avg_value'] == 13.75

    # Category B: 20, 25, 22 -> Sum: 67, Avg: 22.33...
    assert result.loc[1, 'total_value'] == 67
    assert abs(result.loc[1, 'avg_value'] - 22.333333) < 0.001

def test_multi_column_group_by(sample_dataframe):
    """Tests GROUP BY on multiple columns."""
    parsed_sql = {
        "properties": [
            "Category",
            "Region",
            {"aggregate": {"func": "MAX", "col": "Value"}, "alias": "max_val"}
        ],
        "group_by": ["Category", "Region"]
    }
    result = execute_local_query(sample_dataframe, parsed_sql)
    assert list(result.columns) == ['Category', 'Region', 'max_val']
    assert len(result) == 6 # 3 categories * 2 regions

    # Find specific group result
    north_a = result[(result['Category'] == 'A') & (result['Region'] == 'North')]
    assert north_a['max_val'].iloc[0] == 15 # Values for A-North are 10, 15

def test_missing_group_by_column(sample_dataframe):
    """Tests that an error is raised if a grouping column is missing."""
    parsed_sql = {
        "properties": [],
        "group_by": ["NonExistentColumn"]
    }
    with pytest.raises(SQLTranslationError, match="Grouping columns not found"):
        execute_local_query(sample_dataframe, parsed_sql)

def test_missing_aggregate_column(sample_dataframe):
    """Tests that an error is raised if an aggregation column is missing."""
    parsed_sql = {
        "properties": [{"aggregate": {"func": "SUM", "col": "NonExistent"}, "alias": "sum_val"}],
        "group_by": ["Category"]
    }
    with pytest.raises(SQLTranslationError, match="Column 'NonExistent' for aggregation not found"):
        execute_local_query(sample_dataframe, parsed_sql)

def test_unsupported_aggregate_function(sample_dataframe):
    """Tests that an error is raised for an unsupported function."""
    parsed_sql = {
        "properties": [{"aggregate": {"func": "STDEV", "col": "Value"}, "alias": "stdev_val"}],
        "group_by": ["Category"]
    }
    with pytest.raises(SQLTranslationError, match="Unsupported aggregate function: STDEV"):
        execute_local_query(sample_dataframe, parsed_sql)

def test_empty_dataframe():
    """Tests that the function handles an empty DataFrame gracefully."""
    empty_df = pd.DataFrame({'Category': [], 'Value': []})
    parsed_sql = {
        "properties": [
            "Category",
            {"aggregate": {"func": "COUNT", "col": "*"}, "alias": "count_all"}
        ],
        "group_by": ["Category"]
    }
    result = execute_local_query(empty_df, parsed_sql)
    assert result.empty
    assert isinstance(result, pd.DataFrame)
from notion_db_connector.local_engine import execute_local_join

@pytest.fixture
def users_df():
    """DataFrame representing a 'users' table."""
    data = {
        'user_id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'city': ['A', 'B', 'A', 'C']
    }
    return pd.DataFrame(data)

@pytest.fixture
def orders_df():
    """DataFrame representing an 'orders' table."""
    data = {
        'order_id': [101, 102, 103, 104, 105],
        'customer_id': [1, 2, 1, 3, 5], # User 5 doesn't exist in users_df
        'amount': [100, 150, 200, 50, 75]
    }
    return pd.DataFrame(data)

def test_inner_join(users_df, orders_df):
    """Tests a standard INNER JOIN."""
    join_info = {
        "join_type": "inner",
        "left_on": "user_id",
        "right_on": "customer_id"
    }
    result = execute_local_join(users_df, orders_df, join_info)
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4 # Should match orders from users 1, 2, 3
    assert 'user_id' in result.columns
    assert 'customer_id' in result.columns
    assert 'name' in result.columns
    assert 'amount' in result.columns
    # Check that a row for a known user is present
    assert 'Alice' in result['name'].values
    assert result[result['name'] == 'Alice']['amount'].sum() == 300 # 100 + 200

def test_left_join(users_df, orders_df):
    """Tests a LEFT JOIN, keeping all users."""
    join_info = {
        "join_type": "left",
        "left_on": "user_id",
        "right_on": "customer_id"
    }
    result = execute_local_join(users_df, orders_df, join_info)

    assert len(result) == 5 # 4 users, Alice has 2 orders
    # David (user_id 4) should be present, but his order details should be NaN
    david_row = result[result['user_id'] == 4]
    assert not david_row.empty
    assert pd.isna(david_row['order_id'].iloc[0])
    assert pd.isna(david_row['amount'].iloc[0])

def test_join_missing_key(users_df, orders_df):
    """Tests that an error is raised if a join key is missing."""
    join_info = {
        "join_type": "inner",
        "left_on": "non_existent_key",
        "right_on": "customer_id"
    }
    with pytest.raises(SQLTranslationError, match="Join key 'non_existent_key' not found"):
        execute_local_join(users_df, orders_df, join_info)

    join_info_right = {
        "join_type": "inner",
        "left_on": "user_id",
        "right_on": "non_existent_key"
    }
    with pytest.raises(SQLTranslationError, match="Join key 'non_existent_key' not found"):
        execute_local_join(users_df, orders_df, join_info_right)