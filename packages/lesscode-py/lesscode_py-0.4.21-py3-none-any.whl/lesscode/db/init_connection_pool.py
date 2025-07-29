# -*- coding: utf-8 -*-

from tornado.options import options, define

from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode

define("database", default={}, type=dict, help="数据库链接资源池,内部使用")
define("conn_info", default=None, type=list, help="数据库链接信息")


class InitConnectionPool:
    """
    初始化连接池
    """

    @staticmethod
    async def create_pool():
        """
        获取配置的链接信息，生成对应的连接池
        :return:
        """
        if options.conn_info:
            for conn_info in options.conn_info:
                if conn_info.enable:
                    if options.database.keys().__contains__(conn_info.name):
                        # 相同key的连接池已经存在，抛出异常
                        raise BusinessException(StatusCode.RESOURCE_EXIST(f"{conn_info.name}连接池"))
                    pool = None
                    # 依据数据库类型进行链接池创建
                    if conn_info.dialect == "postgresql":
                        clazz = InitConnectionPool.getClass("lesscode.db.postgresql.postgresql_pool",
                                                            fromlist="PostgresqlPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "mysql":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.mysql.mysql_pool", fromlist="MysqlPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "clickhouse":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.clickhouse.clickhouse_pool",
                                                            fromlist="ClickhousePool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "dm":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.dm.dm_pool", fromlist="DmPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "generic":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.generic.generic_pool", fromlist="GenericPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "mongodb":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.mongodb.mongodb_pool", fromlist="MongodbPool")
                        # 执行用例
                        pool = clazz(conn_info).create_pool()
                    elif conn_info.dialect == "elasticsearch":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.elasticsearch.elasticsearch_pool",
                                                            fromlist="ElasticsearchPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "esapi":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.es.es_pool", fromlist="EsPool")
                        # 执行用例
                        pool = clazz(conn_info).create_pool()
                    elif conn_info.dialect == "redis":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.redis.redis_pool", fromlist="RedisPool")
                        # 执行用例
                        pool = clazz(conn_info).create_pool()
                    elif conn_info.dialect == "neo4j":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.neo4j.neo4j_pool", fromlist="Neo4jPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    elif conn_info.dialect == "sqlalchemy":
                        clazz = InitConnectionPool.getClass("lesscode.db.sqlalchemy.sqlalchemy_pool",
                                                            fromlist="SqlAlchemyPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "nebula":
                        clazz = InitConnectionPool.getClass("lesscode.db.nebula.nebula_pool",
                                                            fromlist="NebulaPool")
                        # 执行用例
                        pool = clazz(conn_info).create_pool()
                    elif conn_info.dialect == "redis-cluster":
                        clazz = InitConnectionPool.getClass("lesscode.db.redis_cluster.redis_cluster_pool",
                                                            fromlist="RedisClusterPool")
                        # 执行用例
                        pool = await clazz(conn_info).create_pool()
                    if pool:
                        options.database[conn_info.name] = (pool, conn_info)

    @staticmethod
    def sync_create_pool():
        """
                获取配置的链接信息，生成对应的连接池
                :return:
                """
        if options.conn_info:
            for conn_info in options.conn_info:
                if conn_info.enable:
                    if options.database.keys().__contains__(conn_info.name):
                        # 相同key的连接池已经存在，抛出异常
                        raise BusinessException(StatusCode.RESOURCE_EXIST(f"{conn_info.name}连接池"))
                    pool = None
                    # 依据数据库类型进行链接池创建
                    if conn_info.dialect == "postgresql":
                        clazz = InitConnectionPool.getClass("lesscode.db.postgresql.postgresql_pool",
                                                            fromlist="PostgresqlPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "mysql":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.mysql.mysql_pool", fromlist="MysqlPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "clickhouse":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.clickhouse.clickhouse_pool",
                                                            fromlist="ClickhousePool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "dm":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.dm.dm_pool", fromlist="DmPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "generic":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.generic.generic_pool", fromlist="GenericPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "mongodb":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.mongodb.mongodb_pool", fromlist="MongodbPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "elasticsearch":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.elasticsearch.elasticsearch_pool",
                                                            fromlist="ElasticsearchPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "esapi":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.es.es_pool", fromlist="EsPool")
                        # 执行用例
                        pool = clazz(conn_info).create_pool()
                    elif conn_info.dialect == "redis":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.redis.redis_pool", fromlist="RedisPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "neo4j":
                        # 获取包中用例的函数引用
                        clazz = InitConnectionPool.getClass("lesscode.db.neo4j.neo4j_pool", fromlist="Neo4jPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "sqlalchemy":
                        clazz = InitConnectionPool.getClass("lesscode.db.sqlalchemy.sqlalchemy_pool",
                                                            fromlist="SqlAlchemyPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "nebula":
                        clazz = InitConnectionPool.getClass("lesscode.db.nebula.nebula_pool",
                                                            fromlist="NebulaPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    elif conn_info.dialect == "redis-cluster":
                        clazz = InitConnectionPool.getClass("lesscode.db.redis_cluster.redis_cluster_pool",
                                                            fromlist="RedisClusterPool")
                        # 执行用例
                        pool = clazz(conn_info).sync_create_pool()
                    if pool:
                        options.database[conn_info.name] = (pool, conn_info)

    @staticmethod
    def getClass(name, fromlist):
        return getattr(__import__(name, fromlist=fromlist), fromlist)
    # @staticmethod
    # async def create_pool_postgresql(conn_info: ConnectionInfo):
    #     """
    #     创建postgresql 异步连接池
    #     :param conn_info: 连接信息
    #     :return: AsyncConnectionPool
    #     """
    #     if conn_info.async_enable:
    #         from aiopg import create_pool
    #         pool = await create_pool(host=conn_info.host, port=conn_info.port, user=conn_info.user,
    #                                  password=conn_info.password,
    #                                  database=conn_info.db_name)
    #         return pool
    #     else:
    #         raise NotImplementedError

    # @staticmethod
    # async def create_pool_mysql(conn_info: ConnectionInfo):
    #     """
    #     创建mysql 异步连接池
    #     :param conn_info: 连接信息
    #     :return:
    #     """
    #     if conn_info.async_enable:
    #         import aiomysql
    #         pool = await aiomysql.create_pool(host=conn_info.host, port=conn_info.port, user=conn_info.user,
    #                                           password=conn_info.password, pool_recycle=60,
    #                                           db=conn_info.db_name, autocommit=True, minsize=conn_info.min_size,
    #                                           maxsize=conn_info.max_size)
    #         return pool
    #     else:
    #         raise NotImplementedError

    # @staticmethod
    # def create_pool_mongodb(conn_info: ConnectionInfo):
    #     """
    #     创建mongodb 异步连接池
    #     :param conn_info: 连接信息
    #     :return:
    #     """
    #     if conn_info.async_enable:
    #         import motor
    #         conn_info_string = f"mongodb://{conn_info.user}:{conn_info.password}@{conn_info.host}:{conn_info.port}"
    #         if conn_info.params:
    #             if conn_info.params == "LDAP":
    #                 conn_info_string += "/?authMechanism=PLAIN"
    #             elif conn_info.params == "Password":
    #                 conn_info_string += "/?authSource=admin"
    #             elif conn_info.params == "X509":
    #                 conn_info_string += "/?authMechanism=MONGODB-X509"
    #         pool = motor.motor_tornado.MotorClient(conn_info_string)
    #         return pool
    #     else:
    #         raise NotImplementedError

    # @staticmethod
    # async def create_pool_es(conn_info: ConnectionInfo):
    #     """
    #     创建elasticsearch 异步连接池
    #     :param conn_info: 连接信息
    #     :return:
    #     """
    #     if conn_info.async_enable:
    #         from elasticsearch import AsyncElasticsearch
    #         host_str = conn_info.host.split(",")
    #         hosts = [f"{conn_info.user}:{conn_info.password}@{host}:{conn_info.port}" for host in host_str]
    #         pool = AsyncElasticsearch(hosts=hosts)
    #         return pool
    #     else:
    #         raise NotImplementedError
