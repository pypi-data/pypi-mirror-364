# -*- coding: utf-8 -*-

import logging
import threading

from tornado.options import define, options
from tornado.web import RequestHandler

from lesscode.utils.doc.interface_doc import parser_swagger
from lesscode.utils.upms_util import upms_register, resource_register
from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode

define("route_prefix", default="", type=str, help="路由前缀")


class RouterMapping(list):
    """
    RouterMapping 类用于存储访问路径"URL"与处理器之间对应关系集合
    直接继承list
    """

    _instance_lock = threading.Lock()

    def __init__(self):
        super(RouterMapping, self).__init__()
        # 存放类名、处理方法、url 的元祖集合 url为方法上指定路径
        self.dynamicMethods = []
        # 存放url与具体业务处理方法的映射关系（url，function）
        self.handlerMapping = []

    @classmethod
    def instance(cls):
        if not hasattr(RouterMapping, "_instance"):
            with RouterMapping._instance_lock:
                if not hasattr(RouterMapping, "_instance"):
                    RouterMapping._instance = RouterMapping()
        return RouterMapping._instance


def Handler(url: str, desc=""):
    """
    RequestHandler对应路径注册装饰器，完成处理类与url对应注册。
    :param prefix: 路由前缀
    :param url:
    :return:
    """
    route_prefix = options.route_prefix

    def wrapper(cls):
        # 验证是否为RequestHandler 子类，仅注册其子类
        if not issubclass(cls, RequestHandler):
            raise RuntimeError("Handler注释器只能装饰在RequestHandler子类上")
        # 通过类名查找对应该类下的所有注册方法信息
        res = [item for item in RouterMapping.instance().dynamicMethods
               if item[0] == cls.__name__]
        # 资源注册
        resource_id = resource_register(resource_type=0, url="", label="接口资源", access=0, parent_id="")
        path_group_list = cls.__module__.split(".")
        if path_group_list[0] == "handlers":
            if desc:
                path_group_list[-1] = desc
            for path in path_group_list[1:]:
                resource_id = resource_register(resource_type=0, url="", label=path, access=0, parent_id=resource_id)
        for item in res:
            # 处理类 RequestHandler 子类 使用时统一继承BaseHandler
            handler = item[1]
            # 全路径 Handler+Mapping 组合
            full_url = route_prefix + url + item[2]
            if options.url_log_enable:
                logging.info(f"url={full_url}")
            # 判断是否存在重复注册情况，重复情况直接抛出异常
            # if [router for router in RouterMapping.instance() if full_url in router]:
            #     raise BusinessException(StatusCode.RESOURCE_EXIST(f'路由"{full_url}"'))
            for router in RouterMapping.instance():
                if full_url == router[0]:
                    raise BusinessException(StatusCode.RESOURCE_EXIST(f'路由"{full_url}"'))
            # 存储URL与 RequestHandler 子类对应关系，用于提供给Tornado注册使用
            RouterMapping.instance().append((full_url, cls))
            # 存储URL与处理方法的对应关系，用于调用分发使用
            RouterMapping.instance().handlerMapping.append((full_url, handler))
            # RouterMapping.instance().handlerMapping.append((full_url, handler))
            upms_register(item, full_url)
            resource_register(resource_type=2, url=item[5], label=item[4], access=item[6], parent_id=resource_id,
                              full_url=full_url)
        cls.__route_name__ = url
        try:
            parser_swagger(cls, desc)
        except Exception as e:
            logging.error(e.args)

        return cls

    return wrapper


def GetMapping(url: str = "", client_name: str = None, title: str = None, en_name: str = None, access: int = 1,
               interface_desc: str = ""):
    """
    用于类名、处理方法、url 的元祖集合注册处理，暂时GetMapping与PostMapping实现保持一致，预留入口为后期扩展提供支持。
    :param interface_desc:
    :param client_name:
    :param access:
    :param en_name:
    :param title:
    :param url:
    :return:
    """

    def wrapper(func):
        # 组合  类名、处理方法、url 的元祖 （url仅代表方法上Mapping装饰器的参数）
        path = url
        if not path:
            path = "/{}".format(func.__name__)
        RouterMapping.instance().dynamicMethods.append(
            (func.__qualname__.replace('.' + func.__name__, ''),
             func, path, client_name, title, en_name, access))
        func.__route_name__ = path
        func.__http_method__ = "get"
        func.__cn_name__ = title
        try:
            parser_swagger(func, (title if title else "") + interface_desc)
        except Exception as e:
            logging.error(e.args)
        return func

    return wrapper


def PostMapping(url: str = "", client_name: str = None, title: str = None, en_name: str = None, access: int = 1,
                interface_desc: str = ""):
    """
    用于类名、处理方法、url 的元祖集合注册处理，暂时GetMapping与PostMapping实现保持一致，预留入口为后期扩展提供支持。
    :param interface_desc:
    :param client_name:
    :param access:
    :param en_name:
    :param title:
    :param url:
    :return:
    """

    def wrapper(func):
        # 组合  类名、处理方法、url 的元祖 （url仅代表方法上Mapping装饰器的参数）
        path = url
        if not path:
            path = "/{}".format(func.__name__)
        RouterMapping.instance().dynamicMethods.append(
            (func.__qualname__.replace('.' + func.__name__, ''),
             func, path, client_name, title, en_name, access))
        func.__route_name__ = path
        func.__http_method__ = "post"
        func.__cn_name__ = title
        try:
            parser_swagger(func, (title if title else "") + interface_desc)
        except Exception as e:
            logging.error(e.args)

        return func

    return wrapper


def PutMapping(url: str = "", client_name: str = None, title: str = None, en_name: str = None, access: int = 1,
               interface_desc: str = ""):
    """
    用于类名、处理方法、url 的元祖集合注册处理，暂时GetMapping与PostMapping实现保持一致，预留入口为后期扩展提供支持。
    :param interface_desc:
    :param client_name:
    :param access:
    :param en_name:
    :param title:
    :param url:
    :return:
    """

    def wrapper(func):
        # 组合  类名、处理方法、url 的元祖 （url仅代表方法上Mapping装饰器的参数）
        path = url
        if not path:
            path = "/{}".format(func.__name__)
        RouterMapping.instance().dynamicMethods.append(
            (func.__qualname__.replace('.' + func.__name__, ''),
             func, path, client_name, title, en_name, access))
        func.__route_name__ = path
        func.__http_method__ = "put"
        func.__cn_name__ = title
        try:
            parser_swagger(func, (title if title else "") + interface_desc)
        except Exception as e:
            logging.error(e.args)

        return func

    return wrapper


def DeleteMapping(url: str = "", client_name: str = None, title: str = None, en_name: str = None, access: int = 1,
                  interface_desc: str = ""):
    """
    用于类名、处理方法、url 的元祖集合注册处理，暂时GetMapping与PostMapping实现保持一致，预留入口为后期扩展提供支持。
    :param interface_desc:
    :param client_name:
    :param access:
    :param en_name:
    :param title:
    :param url:
    :return:
    """

    def wrapper(func):
        # 组合  类名、处理方法、url 的元祖 （url仅代表方法上Mapping装饰器的参数）
        path = url
        if not path:
            path = "/{}".format(func.__name__)
        RouterMapping.instance().dynamicMethods.append(
            (func.__qualname__.replace('.' + func.__name__, ''),
             func, path, client_name, title, en_name, access))
        func.__route_name__ = path
        func.__http_method__ = "delete"
        func.__cn_name__ = title
        try:
            parser_swagger(func, (title if title else "") + interface_desc)
        except Exception as e:
            logging.error(e.args)

        return func

    return wrapper
