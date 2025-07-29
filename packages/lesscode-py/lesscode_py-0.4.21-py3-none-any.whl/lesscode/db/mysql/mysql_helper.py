# -*- coding: utf-8 -*-

from lesscode.db.base_sql_helper import BaseSqlHelper, echo_sql
from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.db.page import Page
from lesscode.db.relational_db_helper import RelationalDbHelper


class MysqlHelper(RelationalDbHelper):
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
        with self.pool.dedicated_connection() as conn:
            conn.ping(reconnect=True)
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
        with self.pool.dedicated_connection() as conn:
            conn.ping(reconnect=True)
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
        with self.pool.dedicated_connection() as conn:
            conn.ping(reconnect=True)
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
        with self.pool.dedicated_connection() as conn:
            conn.ping(reconnect=True)
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
        page_sql = f"SELECT {','.join(cols)} FROM ({query_sql}) cs LIMIT {Page.skip(page_num, page_size)},{page_size}"
        # 组装查询数量语句
        count_sql = f"SELECT count(1) total FROM ({query_sql}) cs"
        return page_sql, values, count_sql
