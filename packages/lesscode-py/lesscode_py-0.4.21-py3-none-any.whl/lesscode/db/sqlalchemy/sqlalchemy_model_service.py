import importlib
from typing import Union

from lesscode.db.ds_helper import DSHelper
from lesscode.db.sqlalchemy.sqlalchemy_helper import SqlAlchemyHelper, result_to_json


class SQLAlchemyModelBaseService:
    __model__ = ""
    __connect_name__ = ""

    @classmethod
    def convert_filter(cls, filter_data: Union[list, dict] = None):
        try:
            sqlalchemy_utils = importlib.import_module("lesscode_utils.sqlalchemy_utils")
        except ImportError:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils==0.0.48")
        filters = []
        if filter_data:
            if isinstance(filter_data, list):
                for field in filter_data:
                    if isinstance(field, dict):
                        _column = field.get('column')
                        _value = field.get('value')
                        _end_value = field.get('end_value')
                        # ["in","like","between","not in","not like","is null","not null","not in list","eq","=","not eq","!=","gt",">","gte",">=","lt","<","lte",">="]
                        _relation = field.get('relation', "in")
                        _position = field.get('position', "LR")
                        sqlalchemy_utils.condition_by_relation(filters, cls.__model__, _column, _relation, _value,
                                                               _end_value,
                                                               _position)
                    elif isinstance(field, list):
                        filters.extend(field)
                    else:
                        filters.append(field)
            elif isinstance(filter_data, dict):
                for field, value in filter_data.items():
                    if value:
                        if isinstance(value, list):
                            sqlalchemy_utils.condition_by_relation(filters, cls.__model__, field, "in", value)
                        elif isinstance(value, dict):
                            _value = value.get('value')
                            _end_value = value.get('end_value')
                            # ["in","like","between","not in","not like","is null","not null","not in list","eq","=","not eq","!=","gt",">","gte",">=","lt","<","lte",">="]
                            _relation = value.get('relation', "in")
                            _position = value.get('position', "LR")
                            sqlalchemy_utils.condition_by_relation(filters, cls.__model__, field, _relation, _value,
                                                                   _end_value,
                                                                   _position)
                        else:
                            sqlalchemy_utils.condition_by_relation(filters, cls.__model__, field, "eq", value)
        return filters

    @classmethod
    def get_schema_names(cls):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        pool = DSHelper(cls.__connect_name__).pool
        inspect = sqlalchemy.inspect(pool)
        names = inspect.get_schema_names()
        return names

    @classmethod
    def get_table_names(cls):
        pool = DSHelper(cls.__connect_name__).pool
        table_names = pool.table_names()
        return table_names

    @classmethod
    def get_table_structure(cls):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        pool = DSHelper(cls.__connect_name__).pool
        database_name = pool.url.database
        inspect = sqlalchemy.inspect(pool)
        foreign_keys = []
        if hasattr(cls.__model__, "__tablename__"):
            table_name = cls.__model__.__tablename__
            if hasattr(cls.__model__, "__table__"):
                t = cls.__model__.__table__
                if hasattr(t, "foreign_keys"):
                    foreign_keys = t.foreign_keys
        else:
            if hasattr(cls.__model__, "name"):
                table_name = cls.__model__.name
                if hasattr(cls.__model__, "foreign_keys"):
                    foreign_keys = cls.__model__.foreign_keys
            else:
                raise Exception(f"cls.__model__={cls.__model__} is error")
        columns = inspect.get_columns(table_name)
        indexes = inspect.get_indexes(table_name)
        primary_key = inspect.get_pk_constraint(table_name)
        column_list = [{"name": _.get("name"),
                        "type": _.get("type").__class__.__name__,
                        "default": _.get("default"),
                        "autoincrement": _.get("autoincrement"),
                        "comment": _.get("comment")}
                       for _ in columns]
        index_list = [{"index_name": _.get("name"), "column_names": _.get("column_names")} for _ in indexes]
        foreign_key_list = [
            {"name": _.parent.name,
             "type": _.column.type.__class__.__name__,
             "target_table": _.column.table.name,
             "target_database_name": _.column.table.schema,
             "target_column": _.column.name
             } for _ in
            foreign_keys]
        table = {
            "database_name": database_name,
            "table_name": table_name,
            "columns": column_list,
            "indexes": index_list,
            "primary_key": primary_key,
            "foreign_keys": foreign_key_list
        }
        return table

    @classmethod
    def count(cls, filter_data: Union[list, dict] = None, find_column: list = None, count_key="count"):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        filters = cls.convert_filter(filter_data)
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            field_list = []
            group_list = []
            if not find_column:
                field_list.append(sqlalchemy.func.count())
                statement = sqlalchemy.select(sqlalchemy.func.count()).select_from(cls.__model__).filter(
                    *filters)
                res = session.execute(statement).scalar()
                return res
            else:
                for _ in find_column:
                    field_list.append(sqlalchemy.column(_))
                    group_list.append(sqlalchemy.column(_))
                field_list.append(sqlalchemy.func.count().label(count_key))
                statement = sqlalchemy.select(*field_list).select_from(cls.__model__).filter(*filters).group_by(
                    *group_list)
                res = session.execute(statement).all()
                return result_to_json(res)

    @classmethod
    def find_one(cls, _id, find_column: list = None):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        filters = [cls.__model__.id == _id]
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            if not find_column:
                statement = sqlalchemy.select(cls.__model__).where(*filters)
                res = session.execute(statement).scalars().first() or {}
            else:
                statement = sqlalchemy.select(*[sqlalchemy.column(_) for _ in find_column]).select_from(
                    cls.__model__).where(*filters)
                res = session.execute(statement).first() or {}
            res = result_to_json(res)
            return res

    @classmethod
    def find_one_by_filed(cls, field: str = None, value: str = None, find_column: list = None):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        filters = []
        if field is not None and value is not None:
            filters.append(getattr(cls.__model__, field) == value)
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            if not find_column:
                statement = sqlalchemy.select(cls.__model__).where(*filters)
                res = session.execute(statement).scalars().first() or {}
            else:
                statement = sqlalchemy.select(*[sqlalchemy.column(_) for _ in find_column]).select_from(
                    cls.__model__).where(*filters)
                res = session.execute(statement).first() or {}
            res = result_to_json(res)
            return res

    @classmethod
    def find_page(cls, filter_data: Union[list, dict] = None, find_column: list = None, sort_list: list = None,
                  page_num: int = 1, page_size: int = 10):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        try:
            sqlalchemy_utils = importlib.import_module("lesscode_utils.sqlalchemy_utils")
        except ImportError:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils==0.0.48")

        filters = cls.convert_filter(filter_data)

        sort_list = sort_list or []
        sort_list = sqlalchemy_utils.single_model_format_order(cls.__model__, sort_list)
        result = {
            "data_list": [],
            "data_count": 0
        }
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            if not find_column:
                statement = sqlalchemy.select(cls.__model__).where(*filters)
                if sort_list:
                    statement = statement.order_by(*sort_list)
                statement = statement.offset((page_num - 1) * page_size).limit(page_size)
                res = session.execute(statement).scalars().all()
            else:
                statement = sqlalchemy.select(*[sqlalchemy.column(_) for _ in find_column]).select_from(
                    cls.__model__).where(*filters)
                if sort_list:
                    statement = statement.order_by(*sort_list)
                statement = statement.offset((page_num - 1) * page_size).limit(page_size)
                res = session.execute(statement).all()
            result["data_list"] = result_to_json(res)

            total_count_statement = sqlalchemy.select(sqlalchemy.func.count()).select_from(cls.__model__).filter(
                *filters)
            total_count_res = session.execute(total_count_statement).scalar()
            result["data_count"] = total_count_res
            return result

    @classmethod
    def find_all(cls, filter_data: Union[list, dict] = None, find_column: list = None, sort_list: list = None):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        try:
            sqlalchemy_utils = importlib.import_module("lesscode_utils.sqlalchemy_utils")
        except ImportError:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils==0.0.48")
        filters = cls.convert_filter(filter_data)
        sort_list = sort_list or []
        sort_list = sqlalchemy_utils.single_model_format_order(cls.__model__, sort_list)
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            if not find_column:
                statement = sqlalchemy.select(cls.__model__).where(*filters)
                if sort_list:
                    statement = statement.order_by(*sort_list)
                res = session.execute(statement).scalars().all()
            else:
                statement = sqlalchemy.select(*[sqlalchemy.column(_) for _ in find_column]).select_from(
                    cls.__model__).where(*filters)
                if sort_list:
                    statement = statement.order_by(*sort_list)
                res = session.execute(statement).all()
            return result_to_json(res)

    @classmethod
    def save(cls, data: dict, primary_key="id"):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            statement = sqlalchemy.insert(cls.__model__).values(**data)
            res = session.execute(statement)
            last_id = res.lastrowid if primary_key not in data else data.get(primary_key)
            return last_id

    @classmethod
    def bulk_save(cls, data: list):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            statement = sqlalchemy.insert(cls.__model__).values(data)
            res = session.execute(statement)
            return res.rowcount

    @classmethod
    def delete(cls, _id: str):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            statement = sqlalchemy.delete(cls.__model__).where(cls.__model__.id == _id)
            res = session.execute(statement)
            return res.rowcount

    @classmethod
    def bulk_delete(cls, filter_data: Union[list, dict] = None):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        filters = cls.convert_filter(filter_data)
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            statement = sqlalchemy.delete(cls.__model__).where(*filters)
            res = session.execute(statement)
            return res.rowcount

    @classmethod
    def update(cls, _id: str, params: dict):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            statement = sqlalchemy.update(cls.__model__).where(
                cls.__model__.id == _id).values(
                **params)
            res = session.execute(statement)
            return res.rowcount

    @classmethod
    def bulk_update(cls, filter_data: Union[list, dict] = None, params: dict = None):
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        filters = cls.convert_filter(filter_data)
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            statement = sqlalchemy.update(cls.__model__).where(*filters).values(
                **params)
            res = session.execute(statement)
            return res.rowcount

    @classmethod
    def bulk_update_mappings(cls, data: list):
        with SqlAlchemyHelper(cls.__connect_name__).make_session() as session:
            session.bulk_update_mappings(cls.__model__, data)
