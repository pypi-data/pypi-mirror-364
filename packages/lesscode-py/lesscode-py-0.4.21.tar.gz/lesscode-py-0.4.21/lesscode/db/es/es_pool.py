# -*- coding: utf-8 -*-
from lesscode.db.base_connection_pool import BaseConnectionPool
from lesscode.db.es.es_request import EsRequest


class EsPool(BaseConnectionPool):
    """
    Elasticsearch 数据库链接创建类
    """

    def create_pool(self):
        """
        创建elasticsearch 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        info = self.conn_info
        if info.async_enable:
            pool = EsRequest(info.host, info.port, info.user, info.password)
            return pool
        else:
            raise NotImplementedError

    def sync_create_pool(self):
        info = self.conn_info
        if info.async_enable:
            pool = EsRequest(info.host, info.port, info.user, info.password)
            return pool
        else:
            raise NotImplementedError
