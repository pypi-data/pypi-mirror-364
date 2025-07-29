import functools
import inspect
import json
import logging
import sys
import traceback
import uuid

from tornado.options import options

from lesscode.db.redis.redis_helper import RedisHelper
from lesscode.task.task_helper import TaskHelper
from lesscode.utils.json import JSONEncoder


def SyncCache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func_name, cache_key = get_cache_key(func, *args, **kwargs)
            data = get_cache_value(cache_key)
            if data is False:
                data = func(*args, **kwargs)
            if options.scheduler_config.get("enable"):
                task_id = uuid.uuid1().hex
                TaskHelper.add_job(func=update_cache, id=task_id, name="同步更新缓存任务",
                                   kwargs={"cache_key": cache_key, "func": func, "args": args, "kwargs": kwargs})
            return data
        except Exception as e:
            logging.exception(e)
            data = func(*args, **kwargs)
        return data

    return wrapper


def get_cache_key(func, *args, **kwargs):
    signature = inspect.signature(func)
    func_name = str(func).split(" ")[1]
    param_values = []
    for i in args:
        param_values.append(str(i))
    for k, v in signature.parameters.items():
        _v = str(v)
        if k in kwargs and k != "self":
            param_values.append(str(kwargs[k]))
    cache_key = "&".join(param_values)
    cache_key = options.route_prefix + "#" + func_name + "#" + cache_key
    return func_name, cache_key


def get_cache_value(cache_key):
    conn_name = options.cache_conn
    if options.cache_enable:
        data = RedisHelper(conn_name).sync_get(cache_key)
        if data:
            value = json.loads(data)
            return value
        else:
            logging.info("cache_key没找到，cache_key={}".format(cache_key))
            return False
    else:
        logging.info("缓存未开启".format(cache_key))
        return False


def update_cache(cache_key, func, args, kwargs):
    data = func(*args, **kwargs)
    insert_or_update_cache(cache_key, data)


def insert_or_update_cache(cache_key, data):
    conn_name = options.cache_conn
    if sys.getsizeof(data) <= 512 * 1024:
        if options.cache_enable:
            try:
                data_str = json.dumps(data, cls=JSONEncoder)
                RedisHelper(conn_name).sync_set(cache_key, data_str, ex=options.sync_cache_ex)
            except:
                logging.error(traceback.format_exc())
