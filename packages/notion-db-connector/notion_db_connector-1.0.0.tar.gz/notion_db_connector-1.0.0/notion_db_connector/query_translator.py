# -*- coding: utf-8 -*-
"""
@author: 乔肃
@file: query_translator.py
@time: 2025/07/24
@description: 将 SQL AST 翻译成 Notion API 调用
"""
from sqlglot import exp

from .exceptions import SQLTranslationError


class QueryTranslator:
    """
    将 sqlglot 表达式树 (AST) 翻译成 Notion API 的参数.
    This is a stateless class; all required context is passed during method calls.
    """

    def __init__(self):
        """Initializes the stateless translator."""
        pass

    def translate(self, expression, db_name_to_id_map: dict, db_schemas: dict):
        """
        翻译主入口.
        """
        if isinstance(expression, exp.Select):
            return self._translate_select(expression, db_name_to_id_map, db_schemas)
        elif isinstance(expression, exp.Insert):
            return self._translate_insert(expression, db_name_to_id_map)
        elif isinstance(expression, exp.Update):
            return self._translate_update(expression, db_name_to_id_map, db_schemas)
        elif isinstance(expression, exp.Delete):
            return self._translate_delete(expression, db_name_to_id_map, db_schemas)
        else:
            raise SQLTranslationError(f"不支持的 SQL 操作: {type(expression).__name__}")

    def _get_database_id(self, expression, db_name_to_id_map: dict):
        """从表达式中提取 database_id"""
        table_name = None
        # For SELECT statements, the table is in the 'from' argument.
        if isinstance(expression, exp.Select):
            if expression.args.get("from"):
                table_name = expression.args["from"].this.this.name
        # For INSERT, UPDATE, DELETE, it's in the 'this' argument.
        elif hasattr(expression, "this") and hasattr(expression.this, "this"):
             table_name = expression.this.this.name

        if not table_name:
            raise SQLTranslationError("无法从 SQL 中提取数据库名称。")

        if table_name not in db_name_to_id_map:
            raise SQLTranslationError(f"未知的数据库名称: '{table_name}'. 请在 client 初始化时提供映射.")
        return db_name_to_id_map[table_name]

    def _translate_select(self, expression: exp.Select, db_name_to_id_map: dict, db_schemas: dict):
        """翻译 SELECT 查询, 支持聚合和 GROUP BY"""
        database_id = self._get_database_id(expression, db_name_to_id_map)
        db_schema = db_schemas.get(database_id, {})

        # 检查 JOIN
        join_expr = expression.args.get('joins')
        if join_expr:
            if len(join_expr) > 1:
                raise SQLTranslationError("只支持单个 JOIN 操作。")
            
            join = join_expr[0]
            right_table_name = join.this.this.name
            right_database_id = db_name_to_id_map.get(right_table_name)
            if not right_database_id:
                raise SQLTranslationError(f"未知的数据库名称: '{right_table_name}'.")

            on_condition = join.args.get('on')
            if not isinstance(on_condition, exp.EQ):
                raise SQLTranslationError("JOIN ON 条件只支持简单的等式 (e.g., table1.col = table2.col).")

            left_on_col = on_condition.left.this.name
            right_on_col = on_condition.right.this.name

            return {
                "operation": "local_join",
                "left_database_id": database_id,
                "right_database_id": right_database_id,
                "join_type": join.args.get('kind', 'inner').lower(),
                "left_on": left_on_col,
                "right_on": right_on_col,
            }

        # 检查 GROUP BY
        group_by_expr = expression.args.get('group')
        has_group_by = group_by_expr is not None
        
        # 检查聚合函数
        select_expressions = []
        has_aggregation = False
        for e in expression.expressions:
            if isinstance(e, exp.Alias):
                alias = e.alias
                inner_expr = e.this
            else:
                alias = None
                inner_expr = e

            if isinstance(inner_expr, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
                has_aggregation = True
                agg_func = inner_expr.__class__.__name__
                
                # Correctly handle COUNT(*) vs COUNT(column)
                if isinstance(inner_expr.this, exp.Star):
                    agg_col = '*'
                elif hasattr(inner_expr, 'this') and inner_expr.this:
                    agg_col = inner_expr.this.this.name
                else:
                    agg_col = '*' # Fallback for safety

                select_expressions.append({
                    "aggregate": {"func": agg_func, "col": agg_col},
                    "alias": alias or f"{agg_col.lower()}_{agg_func.lower()}"
                })
            elif isinstance(inner_expr, exp.Column):
                select_expressions.append(inner_expr.this.name)
            elif isinstance(inner_expr, exp.Star):
                select_expressions.append("*")

        # 如果是聚合查询
        if has_group_by or has_aggregation:
            if not has_group_by and has_aggregation:
                # This check can be relaxed if we want to support aggregations without GROUP BY (e.g., SELECT COUNT(*) FROM table)
                # For now, we keep it for stricter SQL compliance.
                pass

            group_by_cols = [col.this.name for col in group_by_expr.expressions] if has_group_by else []

            return {
                "operation": "local_query",
                "database_id": database_id,
                "properties": select_expressions,
                "group_by": group_by_cols,
                "is_aggregate": True,
            }

        # 翻译 WHERE <conditions>
        filter_obj = None
        if expression.args.get('where'):
            filter_obj = self._translate_where(expression.args['where'].this, db_schema)
        
        # 标准 SELECT 查询
        properties_to_retrieve = None
        if "*" not in select_expressions:
            properties_to_retrieve = select_expressions

        return {
            "operation": "query",
            "database_id": database_id,
            "properties": properties_to_retrieve,
            "filter": filter_obj,
            "is_aggregate": False,
        }

    def _translate_where(self, condition: exp.Expression, db_schema: dict):
        """翻译 WHERE 子句为 Notion Filter Object."""
        if isinstance(condition, exp.And):
            return {
                "and": [
                    self._translate_where(condition.left, db_schema),
                    self._translate_where(condition.right, db_schema),
                ]
            }
        elif isinstance(condition, exp.EQ):
            prop_name = condition.left.this.this
            value = self._translate_literal(condition.right)

            # SPECIAL CASE: 'id' is not a real property, but the page ID.
            if prop_name.lower() == 'id':
                if not isinstance(value, str):
                    raise SQLTranslationError(f"The value for an 'id' lookup must be a string (a page ID).")
                return {"page_id": value}

            if prop_name not in db_schema:
                raise SQLTranslationError(f"Property '{prop_name}' not found in the database schema.")
            
            prop_type = db_schema[prop_name].get("type")

            filter_body = {"property": prop_name}
            if prop_type == "title":
                filter_body["title"] = {"equals": value}
            elif prop_type == "rich_text":
                filter_body["rich_text"] = {"equals": value}
            elif prop_type == "number":
                filter_body["number"] = {"equals": value}
            elif prop_type == "select":
                filter_body["select"] = {"equals": value}
            # Add more type handlers as needed
            else:
                raise SQLTranslationError(f"Unsupported property type '{prop_type}' in WHERE clause for property '{prop_name}'.")

            return filter_body
        else:
            raise SQLTranslationError(f"不支持的 WHERE 条件: {type(condition).__name__}")

    def _translate_literal(self, literal_expr: exp.Literal):
        """Converts a sqlglot Literal to a Python native type."""
        # The `this` attribute holds the raw value.
        value = literal_expr.this

        # sqlglot's is_string is reliable for quoted values.
        if literal_expr.is_string:
            return str(value)

        # For unquoted values, attempt to convert to a number.
        try:
            num = float(value)
            # Return as int if it's a whole number, otherwise float.
            if num.is_integer():
                return int(num)
            return num
        except (ValueError, TypeError):
            # If it can't be a number, treat it as a string.
            return str(value)

    def _translate_insert(self, expression: exp.Insert, db_name_to_id_map: dict):
        """翻译 INSERT 查询"""
        database_id = self._get_database_id(expression, db_name_to_id_map)
        columns = [c.this for c in expression.this.expressions]
        values_tuple = expression.expression.expressions[0] # VALUES (...)
        values = [self._translate_literal(v) for v in values_tuple.expressions]

        if len(columns) != len(values):
            raise SQLTranslationError("INSERT 语句中列的数量和值的数量不匹配.")

        properties = dict(zip(columns, values))

        return {
            "operation": "create_page",
            "database_id": database_id,
            "properties": properties,
        }

    def _translate_update(self, expression: exp.Update, db_name_to_id_map: dict, db_schemas: dict):
        """翻译 UPDATE 查询"""
        database_id = self._get_database_id(expression, db_name_to_id_map)

        # 翻译 SET a=b, c=d
        updates = {}
        for eq_expr in expression.expressions:
            if not isinstance(eq_expr, exp.EQ):
                raise SQLTranslationError("UPDATE 的 SET 子句必须是等式")
            column = eq_expr.left.this.this
            if column.lower() == 'id':
                raise SQLTranslationError("Cannot update the 'id' property. Page IDs are immutable.")
            value = self._translate_literal(eq_expr.right)
            updates[column] = value

        # 翻译 WHERE
        filter_obj = None
        if expression.args.get('where'):
            # For UPDATE, the table name is in the 'this' argument
            db_schema = db_schemas.get(database_id, {})
            filter_obj = self._translate_where(expression.args['where'].this, db_schema)
        else:
            # Notion API 要求更新时必须指定页面，因此 WHERE 是必需的
            raise SQLTranslationError("UPDATE 语句必须包含 WHERE 子句.")


        return {
            "operation": "update_pages",
            "database_id": database_id,
            "filter": filter_obj,
            "properties": updates,
        }

    def _translate_delete(self, expression: exp.Delete, db_name_to_id_map: dict, db_schemas: dict):
        """翻译 DELETE 查询"""
        database_id = self._get_database_id(expression, db_name_to_id_map)

        # 翻译 WHERE
        filter_obj = None
        if expression.args.get('where'):
            db_schema = db_schemas.get(database_id, {})
            filter_obj = self._translate_where(expression.args['where'].this, db_schema)
        else:
            raise SQLTranslationError("DELETE 语句必须包含 WHERE 子句.")

        return {
            "operation": "delete_pages",
            "database_id": database_id,
            "filter": filter_obj,
        }
