# -*- coding: utf-8 -*-
"""
@author: 乔肃
@file: sql_parser.py
@time: 2025/07/24
@description: SQL 解析器，负责将 SQL 字符串解析为 AST
"""
import sqlglot
from sqlglot import exp

from .exceptions import SQLParsingError


def parse_sql(sql: str):
    """
    解析 SQL 查询字符串.

    :param sql: 原始 SQL 字符串.
    :return: 解析后的表达式树.
    :raises SQLParserError: 如果 SQL 语法无效.
    """
    try:
        # 解析单个表达式
        expressions = sqlglot.parse(sql)
        if len(expressions) != 1:
            raise SQLParserError(f"仅支持单个 SQL 语句, 但检测到 {len(expressions)} 个.")
        return expressions[0]
    except Exception as e:
        raise SQLParsingError(f"SQL 解析失败: {e}") from e
