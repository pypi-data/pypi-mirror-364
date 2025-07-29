import re
from abc import ABCMeta
from typing import List, Any, Union

from lesscode.db.ds_helper import DSHelper


def to_camel_case(x):
    """转驼峰法命名"""
    return re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)


def to_upper_camel_case(x):
    """转大驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].upper() + s[1:]


def to_lower_camel_case(x):
    """转小驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].lower() + s[1:]


def model2dict(model: Union[list, dict]):
    def _2dict(obj):
        if isinstance(obj, dict):
            _data_dict = dict()
            for k, v in vars(obj).items():
                if not k.startswith("__"):
                    _data_dict.update({k: v})
            return _data_dict
        else:
            return [_2dict(_) for _ in model]

    return _2dict(model)


class MongoBaseModel(metaclass=ABCMeta):
    __connect_name__ = ""
    __route_key__ = ""

    def __init__(self, **kwargs):
        pass

    @classmethod
    def database_names(cls):
        pool = DSHelper(cls.__connect_name__).pool
        database_names = pool.database_names()
        return database_names

    @classmethod
    def list_collection_names(cls, database_name=None):
        pool = DSHelper(cls.__connect_name__).pool
        if database_name is None:
            database_name, _ = cls.__route_key__.split(".")
        return pool.list_collection_names(database_name)

    @classmethod
    def count(cls, query: dict):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        total = collection.count_documents(query)
        return total

    @classmethod
    def query_one(cls, query, find_column: Union[dict, list] = None, to_model: bool = False):
        if find_column:
            if isinstance(find_column, list):
                find_column = {_: 1 for _ in find_column}
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        res = collection.find_one(query, find_column)
        if to_model and res:
            res = dict2model(res, cls)
        return res

    @classmethod
    def query_page(cls, query: dict, find_column: Union[dict, list] = None, page_num: int = 1, page_size: int = 10,
                   sort_list: List[List[Any]] = None, to_model: bool = False):
        if find_column:
            if isinstance(find_column, list):
                find_column = {_: 1 for _ in find_column}
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        total = collection.count_documents(query)
        res = collection.find(query, find_column)
        if sort_list:
            res = res.sort(sort_list)
        res = res.skip((page_num - 1) * page_size).limit(page_size)
        if res and to_model:
            res = [dict2model(_, cls) for _ in res]
        else:
            res = list(res)
        return {"data_count": total, "data_list": res}

    @classmethod
    def query_all(cls, query: dict, find_column: Union[dict, list] = None,
                  sort_list: List[List[Any]] = None, to_model: bool = False):
        if find_column:
            if isinstance(find_column, list):
                find_column = {_: 1 for _ in find_column}
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        res = collection.find(query, find_column)
        if sort_list:
            res = res.sort(sort_list)
        if res and to_model:
            res = [dict2model(_, cls) for _ in res]
        else:
            res = list(res)
        return res

    @classmethod
    def insert_one(cls, document):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.insert_one(document=document)

    @classmethod
    def insert_many(cls, data: List[dict]):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.insert_many(documents=data)

    @classmethod
    def delete_one(cls, query):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.delete_one(query)

    @classmethod
    def delete_many(cls, query):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.delete_many(query)

    @classmethod
    def update_one(cls, query, update, upsert=False, **kwargs):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.update_one(filter=query, update=update, upsert=upsert, **kwargs)

    @classmethod
    def update_many(cls, query, update, upsert=False, **kwargs):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.update_many(filter=query, update=update, upsert=upsert, **kwargs)

    @classmethod
    def aggregate(cls, pipeline, **kwargs):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.aggregate(pipeline=pipeline, **kwargs)

    @classmethod
    def bulk_write(cls, data: list, ordered: bool = True, **kwargs):
        pool = DSHelper(cls.__connect_name__).pool
        database_name, collection_name = cls.__route_key__.split(".")
        collection = pool[database_name][collection_name]
        return collection.bulk_write(requests=data, ordered=ordered, **kwargs)


def dict2model(data: dict, model):
    if issubclass(model, MongoBaseModel):
        return model(**data)
    else:
        raise Exception(f"{model.__class__.__name__} is not subclass of BaseModel")


class MongoBaseModelService:
    def __init__(self, connect_name, route_key):
        self.connect_name = connect_name
        self.route_key = route_key

    def get_model(self) -> MongoBaseModel:
        class _BaseModel(MongoBaseModel):
            def __init__(self, connect_name: str, route_key: str, **kwargs):
                super().__init__(**kwargs)
                self.__class__.__connect_name__ = connect_name
                self.__class__.__route_key__ = route_key

        _base_mode = _BaseModel(connect_name=self.connect_name, route_key=self.route_key)
        return _base_mode
