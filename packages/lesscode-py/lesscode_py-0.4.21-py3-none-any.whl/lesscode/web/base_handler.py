# -*- coding: utf-8 -*-

import importlib
import inspect
import json
import logging
import time
import traceback
import types
import uuid
from contextlib import contextmanager
from datetime import datetime
from threading import Thread
from typing import Optional, Awaitable, Any
from urllib.parse import unquote

from tornado import httputil
from tornado.escape import utf8
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.web import RequestHandler, Application

from lesscode.task.task_helper import TaskHelper
from lesscode.utils.CacheUtil import async_common_cache, common_cache
from lesscode.utils.custom_type import User
from lesscode.utils.es_log.record_log import es_record_log
from lesscode.utils.json import JSONEncoder
from lesscode.utils.request import sync_common_request_origin
from lesscode.web.business_exception import BusinessException
from lesscode.web.response_result import ResponseResult
from lesscode.web.router_mapping import RouterMapping
from lesscode.web.status_code import StatusCode


class BaseHandler(RequestHandler):
    """
    BaseHandler 类继承自RequestHandler 用于公共基础功能实现，所有均使用此类为基类，只有使用此类的Handler 会被自动加载
    """

    def __init__(self, application: "Application", request: httputil.HTTPServerRequest, **kwargs):
        """
        初始化方法，完成映射装配
        :param application:
        :param request:
        :param kwargs:
        """
        # 如果想要使用自定义响应，设置self.original为True
        self.start_time = int(round(time.time() * 1000))
        self.end_time = int(round(time.time() * 1000))
        self._request_id = f"self-{uuid.uuid1().hex}"
        self.original = False
        super().__init__(application, request, **kwargs)
        self.command_map = {}
        methods = self.methods()
        for i in range(len(methods)):
            method = getattr(self, methods[i])
            if getattr(method, "__http_method__", None):
                self.command_map[method.__name__] = method

    def methods(self):
        return (list(filter(
            lambda m: not m.startswith("__") and not m.startswith("_") and callable(getattr(self, m)) and
                      type(getattr(self, m, None)) == types.MethodType,
            self.__dir__())))

    def process_request(self, request):
        """
        预处理请求中间件，对请求内容进行改写
        :param request:
        :return:
        """
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        视图中间件，对视图进行处理
        :param request:
        :param view_func:
        :param view_args:
        :param view_kwargs:
        :return:
        """
        pass

    def process_exception(self, exception: Exception):
        """
        异常处理中间件
        :param exception:
        :return:
        """
        raise exception

    def process_response(self, data):
        """
        处理响应数据的中间件
        :param data:
        :return:
        """
        if data is not None:
            self.write(json.dumps(ResponseResult(data=data), ensure_ascii=False, cls=JSONEncoder))

    @contextmanager
    def make_sqlalchemy_session(self, pool, **kwargs):
        try:
            sqlalchemy_orm = importlib.import_module("sqlalchemy.orm")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        session = None
        try:
            pool, _ = options.database[pool]
            db_session = sqlalchemy_orm.scoped_session(sqlalchemy_orm.sessionmaker(bind=pool, **kwargs))
            session = db_session()
            yield session
        except Exception:
            if session:
                session.rollback()
            raise
        else:
            session.commit()
        finally:
            if session:
                session.close()

    async def get(self):
        """
        重写父类get请求处理方法，直接调用post方法统一处理
        :return:
        """
        logging.info(f"Request-Id: {self.request.headers.get('Request-Id', self._request_id)}")
        self.process_request(self.request)
        await self.request_handler()

    async def post(self):
        """
        重写父类post请求方法，使其支持通过URL进行方法调用
        改造Tornado 调用处理方式，不在是一个url对应一个类处理，而是使用同实体处理放到一个类中
        通过不同的url指向不同处理方法
        :return:
        """
        logging.info(f"Request-Id: {self.request.headers.get('Request-Id', self._request_id)}")
        self.process_request(self.request)
        await self.request_handler()

    async def options(self):
        """
        解决跨域验证请求
        HTTP的204(No Content)响应, 就表示执行成功, 但是没有数据
        :return:
        """
        self.set_status(204)
        await self.finish()

    async def put(self):
        """
        重写父类put请求方法，使其支持通过URL进行方法调用
        改造Tornado 调用处理方式，不在是一个url对应一个类处理，而是使用同实体处理放到一个类中
        通过不同的url指向不同处理方法
        :return:
        """
        logging.info(f"Request-Id: {self.request.headers.get('Request-Id', self._request_id)}")
        self.process_request(self.request)
        await self.request_handler()

    async def delete(self):
        """
        重写父类delete请求方法，使其支持通过URL进行方法调用
        改造Tornado 调用处理方式，不在是一个url对应一个类处理，而是使用同实体处理放到一个类中
        通过不同的url指向不同处理方法
        :return:
        """
        logging.info(f"Request-Id: {self.request.headers.get('Request-Id', self._request_id)}")
        self.process_request(self.request)
        await self.request_handler()

    async def patch(self):
        """
        重写父类delete请求方法，使其支持通过URL进行方法调用
        改造Tornado 调用处理方式，不在是一个url对应一个类处理，而是使用同实体处理放到一个类中
        通过不同的url指向不同处理方法
        :return:
        """
        logging.info(f"Request-Id: {self.request.headers.get('Request-Id', self._request_id)}")
        self.process_request(self.request)
        await self.request_handler()

    async def request_handler(self):
        # 通过url路径获取对应的处理方法
        res = [item for item in RouterMapping.instance().handlerMapping
               if item[0] == self.request.path]
        if res:
            # 元组中索引0 存放url，索引 1 存放处理方法对象，此处获取方法对象
            handler_method = res[0][1]
            # 最终整理后的请求参数集合
            # params_list = []
            params_dict = {}
            # 获取当前请求的Content-Type
            content_type = self.request.headers.get('Content-Type')
            # 当前请求参数
            arguments = {}
            query_arguments = self.request.query_arguments
            arguments.update(query_arguments)
            if content_type:
                if "application/json" in content_type:
                    request_body = self.request.body
                    if request_body:
                        body_arguments = json.loads(self.request.body.decode())
                        arguments.update(body_arguments)
                else:
                    body_arguments = self.request.body_arguments
                    arguments.update(body_arguments)
            # 获取处理方法的 参数签名
            signature = inspect.signature(handler_method)
            # parameterName 参数名称, parameter 参数对象
            for parameter_name, parameter in signature.parameters.items():
                # 如果参数是self 做特殊处理，传入本身
                if parameter_name == 'self':
                    # params_list.append(self)
                    params_dict.update({"self": self})
                else:
                    # 依据参数名称，获取请求参数值
                    argument_value = arguments.get(parameter_name)
                    # 分以下几种情况，第一种情况 未取得请求参数
                    if argument_value is None:
                        # 查看是否有默认值，如果有直接跳过即可
                        if parameter.default is not inspect.Parameter.empty:
                            # params_list.append(parameter.default)
                            params_dict.update({parameter_name: parameter.default})
                            continue
                        else:
                            # 如果没有有默认值，要抛出异常 提示"请求缺少必要参数"
                            raise BusinessException(StatusCode.REQUIRED_PARAM_IS_EMPTY(parameter_name))
                    # 获取形参类型
                    parameter_type = parameter.annotation
                    # 形参类型为空，尝试获取形参默认值类型
                    if parameter_type is inspect.Parameter.empty:
                        # if parameter.default is inspect.Parameter.empty:
                        #     parameter_type = type(parameter.default)
                        # else:
                        parameter_type = type(parameter.default)
                    # # 获取实参类型
                    # argument_type = type(argument_value)
                    if isinstance(argument_value, list):  # 如果参数是集合类型要进行遍历并进行转码
                        if self.request.method == "GET":
                            if len(argument_value) == 1:
                                # 仅一个 直接存入
                                # params_list.append(parse_val(argument_value[0], parameter_type))
                                params_dict.update({parameter_name: parse_val(argument_value[0], parameter_type)})
                            else:
                                # 多个要使用集合存入
                                # params_list.append([parse_val(v, parameter_type) for v in argument_value])
                                params_dict.update(
                                    {parameter_name: [parse_val(v, parameter_type) for v in argument_value]})
                        else:
                            # params_list.append([parse_val(v, parameter_type) for v in argument_value])
                            params_dict.update({parameter_name: [parse_val(v, parameter_type) for v in argument_value]})
                    else:
                        # params_list.append(parse_val(argument_value, parameter_type))
                        params_dict.update({parameter_name: parse_val(argument_value, parameter_type)})
            title = handler_method.__cn_name__ or handler_method.__route_name__
            if options.operate_log_enable:
                _user = self.get_current_user()
                _user_id = None
                _username = None
                _phone_no = None
                if _user:
                    _user_id = _user.id
                    _username = _user.username
                    _phone_no = _user.phone_no
                try:
                    _params = dict()
                    for k, v in params_dict.items():
                        if "self" != k:
                            _params[k] = v
                    if options.operate_log_write_method == "api":
                        t = Thread(target=sync_common_request_origin, kwargs={
                            "url": options.write_operate_log_url,
                            "method": "POST",
                            "json": {
                                "operate_action": title,
                                "operate_url": self.request.path,
                                "operate_user_id": _user_id,
                                "operate_user_username": _username,
                                "params": _params,
                                "operate_user_phone_no": _phone_no
                            }
                        })
                        t.start()
                        logging.info(f"添加操作日志，url:{self.request.path},title={title}")
                    elif options.operate_log_write_method == "function":
                        t = Thread(target=options.operate_log_write_func, kwargs={
                            "operate_id": uuid.uuid1().hex,
                            "operate_action": title,
                            "operate_url": self.request.path,
                            "operate_user_id": _user_id,
                            "operate_user_username": _username,
                            "params": _params,
                            "operate_user_phone_no": _phone_no
                        })
                        t.start()
                        logging.info(f"添加操作日志，url:{self.request.path},title={title}")

                except Exception as e:
                    logging.error(f"添加操作日志失败，url={self.request.path},错误信息:{e}")
            # 判断是否为异步非阻塞方法，true 则直接调用
            try:
                if inspect.iscoroutinefunction(handler_method):
                    # data = await handler_method(*params_list)
                    if options.global_cache_enable:
                        data = await async_common_cache(handler_method, options.global_cache_ex, **params_dict)
                    else:
                        data = await handler_method(**params_dict)

                else:
                    # 阻塞方法异步调用
                    # data = await IOLoop.current().run_in_executor(None, handler_method, *params_list)
                    if options.global_cache_enable:
                        func = lambda: common_cache(handler_method, options.global_cache_ex, **params_dict)
                    else:
                        func = lambda: handler_method(**params_dict)
                    data = await IOLoop.current().run_in_executor(None, func)
                self.end_time = int(round(time.time() * 1000))
                self.set_header("Api-Time", f"{self.end_time - self.start_time}ms")
                self.process_response(data)
                if options.scheduler_config.get("enable"):
                    task_id = uuid.uuid1().hex
                    TaskHelper.add_job(es_record_log, id=task_id, name=task_id,
                                       kwargs={"request": self.request, "message": "", "level": "info",
                                               "status_code": "00000", "task_id": task_id})
            except Exception as e:
                self.process_exception(e)

        else:
            raise BusinessException(StatusCode.RESOURCE_NOT_FOUND)

    def set_default_headers(self):
        """ 设置header参数
            重写父类方法
        :return:
        """
        if not options.cors:
            origin = self.request.headers.get("Origin")
            if origin:
                self.set_header("Access-Control-Allow-Origin", origin)
            else:
                self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Request-Id", self.request.headers.get("Request-Id", self._request_id))
            self.set_header("Plugin-Running-Time", self.request.headers.get("Plugin-Running-Time", ""))
            self.set_header("Access-Control-Allow-Headers",
                            "x-requested-with,Authorization,Can-read-cache,Content-Type,User")
            self.set_header("Access-Control-Allow-Methods", "POST,GET,PUT,DELETE,OPTIONS")
            self.set_header("Access-Control-Expose-Headers", "Access-Token")
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        else:
            origin = self.request.headers.get("Origin")
            if origin:
                self.set_header("Access-Control-Allow-Origin", origin)
            else:
                self.set_header("Access-Control-Allow-Origin", "*")
            for key, value in options.cors.items():
                self.set_header(key, value)

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """
        RequestHandler 类中的抽象方法，此处为空实现，解决所有子类都需要继承ABC的问题
        :param chunk:
        :return:
        """
        pass

    def write_error(self, status_code: int, **kwargs) -> None:
        """ 统一处理异常信息返回
        重写父类错误信息函数，业务逻辑代码中引发的异常 在参数对象中exc_info 获取异常信息对象
        :param status_code:
        :param kwargs:
        :return:
        """
        if options.scheduler_config.get("enable"):
            task_id = uuid.uuid1().hex
            TaskHelper.add_job(es_record_log, id=task_id, name=task_id,
                               kwargs={"request": self.request, "message": traceback.format_exc(), "level": "error",
                                       "status_code": status_code, "task_id": task_id})
        error = kwargs["exc_info"]
        if isinstance(error[1], BusinessException):
            self.set_status(200)
            self.write(json.dumps(ResponseResult(status_code=error[1].status_code), ensure_ascii=False))
        else:
            # for line in traceback.format_exception(*kwargs["exc_info"]):
            #     self.write(line)
            self.write(json.dumps(ResponseResult(StatusCode.INTERNAL_SERVER_ERROR(error[1])), ensure_ascii=False))
        self.finish()

    def _request_summary(self):
        """ 设置请求日志记录格式
        重写父类方法。
        :return:
        """
        return "%s %s %s %s %s" % (
            self.request.method, self.request.path, self.request.arguments, self.request.remote_ip,
            self.request.headers.get("User-Agent") or self.request.headers.get("user-agent"))

    def get_current_user(self) -> Any:
        """
        获取当前用户信息
        :return:
        """
        if not options.custom_current_user_switch:
            user_json = self.request.headers.get("User")
            if user_json:
                # TODO 未做加密
                user_info = json.loads(user_json)
                if user_info and isinstance(user_info, dict):
                    user = User()
                    for key in user_info:
                        value = user_info.get(key)
                        if value and isinstance(value, str):
                            user_info[key] = unquote(value)
                        if key == "roleIds" and value and isinstance(value, str):
                            user_info[key] = json.loads(value)
                        setattr(user, key, user_info[key])

                    return user
        else:
            return options.custom_current_user_func(self)
        return None

    def redirect(self, url: str, permanent: bool = False, status: int = None) -> None:
        """Sends a redirect to the given (optionally relative) URL.

        If the ``status`` argument is specified, that value is used as the
        HTTP status code; otherwise either 301 (permanent) or 302
        (temporary) is chosen based on the ``permanent`` argument.
        The default is 302 (temporary).
        """
        if self._headers_written:
            raise Exception("Cannot redirect after headers have been written")
        if status is None:
            status = 301 if permanent else 302
        else:
            assert isinstance(status, int) and 300 <= status <= 399
        self.set_status(status)
        self.set_header("Location", utf8(url))

    def add_create_info(self, data):
        user: User = self.get_current_user()
        if user:
            data["create_user_id"] = user.id
            data["create_user_name"] = user.username
        data["create_time"] = datetime.now()

    def add_modify_info(self, data):
        user: User = self.get_current_user()
        if user:
            data["modify_user_id"] = user.id
            data["modify_user_name"] = user.username
        data["modify_time"] = datetime.now()


# 解析param
def parse_val(val, val_type):
    # inspect.Parameter.empty <class 'NoneType'>
    # isinstance(parameter.annotation, )
    new_val = val
    if isinstance(val, bytes) or isinstance(val, bytearray):
        new_val = val.decode("utf-8")
    if isinstance(val, list):
        val_list = []
        for item in val:
            val_item = parse_val(item, None)
            val_list.append(val_item)
        if val_type == list:
            return val_list
        else:
            new_val = val_list
    if type(new_val) != val_type:
        if val_type == int:
            return int(new_val)
        elif val_type == str and isinstance(new_val, list):
            return new_val[0]
        elif val_type == dict:
            return json.loads(new_val)
        else:
            return new_val
    return new_val
