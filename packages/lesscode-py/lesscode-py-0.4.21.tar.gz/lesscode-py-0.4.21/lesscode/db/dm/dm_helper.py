# -*- coding: utf-8 -*-

from lesscode.db.base_sql_helper import BaseSqlHelper, echo_sql
from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.db.db_function import DBFunction
from lesscode.db.page import Page
from lesscode.db.relational_db_helper import RelationalDbHelper


class DmlHelper(RelationalDbHelper):

    def prepare_condition_sql(self, conditions: list):
        """
        拼接条件SQL 搜集参数信息
        :param conditions: 条件信息
        :return: 条件sql片段, values 对应参数
        """
        connector = "AND"
        condition_sql = ""
        values = []
        for condition in conditions:
            operator, column, value = condition
            if operator == "OR" or operator == "AND":
                connector = operator
                continue
            if operator == "BETWEEN":
                sql_segment = f'{column} BETWEEN ? AND ?'
            elif operator == "NOT_BETWEEN":
                sql_segment = f'{column} NOT BETWEEN ? AND ?'
            elif operator == "LIKE":
                sql_segment = f'{column} LIKE ?'
                value = f"%{value}%"
            elif operator == "NOT_LIKE":
                sql_segment = f'{column} NOT_LIKE ?'
                value = f"%{value}%"
            elif operator == "LIKE_LEFT":
                sql_segment = f'{column} LIKE ?'
                value = f"{value}%"
            elif operator == "LIKE_RIGHT":
                sql_segment = f'{column} LIKE ?'
                value = f"%{value}"
            elif operator == "IS_NULL":
                sql_segment = f'{column} IS NULL '
            elif operator == "IS_NOT_NULL":
                sql_segment = f'{column} IS NOT NULL '
            elif operator == "IN":
                # 依据字段数组织占位符
                placeholder_str = ','.join('?' for v in range(len(value)))
                sql_segment = f'{column} IN ({placeholder_str})'
            elif operator == "NOT_IN":
                # 依据字段数组织占位符
                placeholder_str = ','.join('?' for v in range(len(value)))
                sql_segment = f'{column} NOT IN ({placeholder_str})'
            else:
                # 操作符号不需要转码的
                sql_segment = f'{column} {operator} ?'
            if condition_sql:
                condition_sql = f"{condition_sql} {connector} {sql_segment}"
            else:
                condition_sql = sql_segment
            if column is not None:
                if isinstance(value, list):
                    values.extend(value)
                else:
                    values.append(value)
        return condition_sql, values

    def prepare_query_sql(self, condition_wrapper: ConditionWrapper):
        """
                获取完整拼接查询SQL
                :param condition_wrapper: 查询条件对象
                :return:sql 查询sql, values 对应参数
                """
        sql = f"SELECT {','.join(condition_wrapper.column)} FROM {condition_wrapper.table} "
        condition_sql, values = self.prepare_condition_sql(condition_wrapper.conditions)
        # 拼接 条件SQL
        if condition_sql:
            sql += f" WHERE {condition_sql}"
        # 拼接 分组SQL
        if condition_wrapper.group:
            group_sql = ""
            if isinstance(condition_wrapper.group, str):
                group_sql = f" GROUP BY {condition_wrapper.group}"
            elif isinstance(condition_wrapper.group, list):
                group_sql = f" GROUP BY {','.join(condition_wrapper.group)}"
            sql += group_sql
        # 拼接 排序SQL
        if condition_wrapper.order:
            sql += f" ORDER BY {','.join([' '.join(item) for item in condition_wrapper.order])}"
        return sql, values

    def prepare_insert_sql(self, table_name: str, item: dict):
        """
        组装插入sql
        :param table_name:
        :param item:
        :return:
        """
        # 组装插入数据字段
        column_str = ','.join(item.keys())
        # 依据字段数组织占位符
        placeholder_items = []
        for v in item.values():
            if isinstance(v, DBFunction):
                placeholder_items.append(v.function_body)
            else:
                placeholder_items.append("?")
        placeholder_str = ','.join(placeholder_items)
        # 组装可执行SQL
        insert_sql = f'INSERT INTO {table_name} ({column_str}) VALUES ({placeholder_str})'
        return insert_sql

    def prepare_update_sql(self, condition_wrapper: ConditionWrapper, param: dict):
        """
        组装更新sql
        :param condition_wrapper:
        :param param:
        :return:
        """
        value_items = []
        placeholder_items = []
        for key in param.keys():
            v = param.get(key)
            if isinstance(v, DBFunction):
                placeholder_items.append(f"{key}={v.function_body}")
                value_items.append(v.value)
            else:
                placeholder_items.append(f"{key}=?")
                value_items.append(v)
        column_sql = ','.join(placeholder_items)
        condition_sql, values = self.prepare_condition_sql(condition_wrapper.conditions)
        update_sql = f'UPDATE {condition_wrapper.table} SET {column_sql} WHERE {condition_sql}'
        return update_sql, value_items + values

    def prepare_delete_sql(self, condition_wrapper: ConditionWrapper):
        """
        组装删除SQl
        :param condition_wrapper:
        :return:
        """
        condition_sql, values = self.prepare_condition_sql(condition_wrapper.conditions)
        delete_sql = f'DELETE FROM {condition_wrapper.table} WHERE {condition_sql}'
        return delete_sql, values

    """
    Mysql数据库操作实现
    """

    @echo_sql
    async def execute_sql(self, sql: str, param=None):
        """
        执行sql 仅返回影响数量
        :param sql:
        :param param:
        :return:
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, param)
        return {"rowcount": cursor.rowcount}

    @echo_sql
    async def executemany_sql(self, sql: str, param=None):
        """
        执行批量sql 仅返回影响数量
        :param sql:
        :param param:
        :return:
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # 执行sql 传入参数
                await cursor.executemany(sql, [tuple(item.values()) for item in param])
        return {"rowcount": cursor.rowcount}

    @echo_sql
    async def execute_fetchone(self, sql: str, param=None):
        """
        查询单条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if param:
                    await cursor.execute(sql, param)
                else:
                    await cursor.execute(sql)
                description = cursor.description
                rs = await cursor.fetchone()
        return BaseSqlHelper.dict_row(description, rs)

    @echo_sql
    async def execute_fetchall(self, sql: str, param=None):
        """
        查询多条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if param:
                    await cursor.execute(sql, param)
                else:
                    await cursor.execute(sql)
                description = cursor.description
                rs = await cursor.fetchall()
        return BaseSqlHelper.dict_row(description, list(rs))

    @echo_sql
    def sync_execute_sql(self, sql: str, param=None):
        """
        执行sql 仅返回影响数量
        :param sql:
        :param param:
        :return:
        """
        sql = sql.replace("%s","?")
        with self.pool.dedicated_connection() as conn:
            conn.ping()
            with conn.cursor() as cursor:
                cursor.execute(sql, param)
        return {"rowcount": cursor.rowcount}

    @echo_sql
    def sync_executemany_sql(self, sql: str, param=None):
        """
        执行批量sql 仅返回影响数量
        :param sql:
        :param param:
        :return:
        """
        sql = sql.replace("%s", "?")
        with self.pool.dedicated_connection() as conn:
            conn.ping()
            with conn.cursor() as cursor:
                cursor.executemany(sql, [tuple(item.values()) for item in param])
        return {"rowcount": cursor.rowcount}

    @echo_sql
    def sync_execute_fetchone(self, sql: str, param=None):
        """
        查询单条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        sql = sql.replace("%s", "?")
        with self.pool.dedicated_connection() as conn:
            conn.ping()
            with conn.cursor() as cursor:
                if param:
                    cursor.execute(sql, param)
                else:
                    cursor.execute(sql)
                description = cursor.description
                rs = cursor.fetchone()
        return BaseSqlHelper.dict_row(description, rs)

    @echo_sql
    def sync_execute_fetchall(self, sql: str, param=None):
        """
        查询多条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        sql = sql.replace("%s", "?")
        with self.pool.dedicated_connection() as conn:
            conn.ping()
            with conn.cursor() as cursor:
                if param:
                    cursor.execute(sql, param)
                else:
                    cursor.execute(sql)
                description = cursor.description
                rs = cursor.fetchall()
        return BaseSqlHelper.dict_row(description, list(rs))

    def prepare_page_sql(self, condition_wrapper: ConditionWrapper, page_num: int, page_size: int):
        """
        获取分页SQL
        :param condition_wrapper: 查询参数
        :param page_num: 当前页
        :param page_size: 每页记录数
        :return:page_sql 分页sql, values 对应参数, count_sql 统计总数sql
        """
        query_sql, values = self.prepare_query_sql(condition_wrapper)
        cols = []
        for col in condition_wrapper.column:
            col = col.upper().replace("AS", "").strip().split(" ")
            cols.append(col[-1].strip())
        # 组装分页查询语句，需要依据页码计算 起始索引
        page_sql = f"SELECT {','.join(cols)} FROM ({query_sql}) cs OFFSET {Page.skip(page_num, page_size)} LIMIT {page_size}"
        # 组装查询数量语句
        count_sql = f"SELECT count(1) total FROM ({query_sql}) cs"
        return page_sql, values, count_sql
