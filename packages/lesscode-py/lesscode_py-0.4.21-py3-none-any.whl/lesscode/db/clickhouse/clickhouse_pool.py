# -*- coding: utf-8 -*-
import importlib

from lesscode.db.base_connection_pool import BaseConnectionPool


class ClickhousePool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    async def create_pool(self):
        """
        创建mysql 异步连接池
        :return:
        """
        try:
            aiomysql = importlib.import_module("aiomysql")
        except ImportError:
            raise Exception(f"pymysql is not exist,run:pip install aiomysql==0.0.22")
        params = self.conn_info.params
        if not isinstance(params, dict):
            params = dict()
        pool_recycle = params.pop("pool_recycle", 3600)
        autocommit = params.pop("autocommit", True)
        if self.conn_info.async_enable:
            pool = await aiomysql.create_pool(host=self.conn_info.host, port=self.conn_info.port,
                                              user=self.conn_info.user,
                                              password=self.conn_info.password,
                                              pool_recycle=pool_recycle,
                                              db=self.conn_info.db_name, autocommit=autocommit,
                                              minsize=self.conn_info.min_size,
                                              maxsize=self.conn_info.max_size, **params)
            return pool
        else:
            raise NotImplementedError

    def sync_create_pool(self):
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise Exception(f"DBUtils is not exist,run:pip install DBUtils==3.0.2")
        try:
            clickhouse_driver = importlib.import_module("clickhouse_driver")
        except ImportError:
            raise Exception(f"clickhouse_driver is not exist,run:pip install clickhouse_driver")
        params = self.conn_info.params
        if not isinstance(params, dict):
            params = dict()

        pool = pooled_db.PooledDB(creator=clickhouse_driver.connect, host=self.conn_info.host, port=self.conn_info.port,
                                  user=self.conn_info.user,
                                  password=self.conn_info.password, database=self.conn_info.db_name or "default",
                                  **params)
        return pool
