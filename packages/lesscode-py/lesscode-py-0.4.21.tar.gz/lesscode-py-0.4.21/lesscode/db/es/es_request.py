# -*- coding: utf-8 -*-
import importlib
import logging
import random
import traceback


class EsRequest:

    def __init__(self, host, port, user, password):

        # 主机地址
        self.host = host
        # 端口号
        self.port = port
        # 用户名
        self.user = user
        # 密码
        self.password = password
        host_str = host.split(",")
        self.hosts = [host for host in host_str]

    def es_selector_way(self, url_func_str, param_dict, find_condition=None, request_way="post"):
        try:
            request = importlib.import_module("lesscode_utils.request")
        except ImportError as e:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils")
        res = None
        # 随机打乱列表
        random.shuffle(self.hosts)
        num = len(self.hosts)
        for i, host in enumerate(self.hosts):
            param_dict["host"] = host
            param_dict["port"] = self.port
            url = url_func_str(**param_dict)
            try:
                if request_way == "get":
                    res = request.sync_common_get(url, params=find_condition, result_type="json",
                                                  auth=request.get_basic_auth(self.user, self.password))
                elif request_way == "post":
                    res = request.sync_common_post(url, json=find_condition, result_type="json",
                                                   auth=request.get_basic_auth(self.user, self.password))
                if res:
                    if res.get("took"):
                        break
            except Exception as e:
                if i == num - 1:
                    raise e
        return res

    def format_es_request(self, url, methd: str, body, params=None):
        """
        发送http请求
        :param params:
        :param url:
        :param body:
        :return:
        """
        try:
            request = importlib.import_module("lesscode_utils.request")
        except ImportError as e:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils")
        res = None
        if methd.lower() == "post":
            res = request.sync_common_post(url, json=body, params=params, headers={'content-type': "application/json"},
                                           result_type="json",
                                           auth=request.get_basic_auth(self.user, self.password), timeout=None)
        elif methd.lower() == "get":
            res = request.sync_common_get(url, json=body, params=params, headers={'content-type': "application/json"},
                                          result_type="json",
                                          auth=request.get_basic_auth(self.user, self.password), timeout=None)
        elif methd.lower() == "put":
            res = request.sync_common_put(url, json=body, params=params, headers={'content-type': "application/json"},
                                          result_type="json",
                                          auth=request.get_basic_auth(self.user, self.password), timeout=None)
        elif methd.lower() == "delete":
            res = request.sync_common_delete(url, json=body, params=params,
                                             headers={'content-type': "application/json"},
                                             result_type="json",
                                             auth=request.get_basic_auth(self.user, self.password), timeout=None)
        return res

    def format_scroll_url(self, host=None, port=None, route_key=None, scroll=None):
        return self.replace_url_kwargs("http://{host}{port}/{route_key}/_search?scroll={scroll}",
                                       {"host": host, "port": port, "route_key": route_key, "scroll": scroll})

    def format_scroll_id_url(self, host=None, port=None, ):
        return self.replace_url_kwargs("http://{host}{port}/_search/scroll",
                                       {"host": host, "port": port})

    def format_es_post_url(self, host=None, port=None, route_key=None):
        return self.replace_url_kwargs("http://{host}{port}/{route_key}/_search",
                                       {"host": host, "port": port, "route_key": route_key})

    def format_url(self, path, host=None, port=None):
        return self.replace_url_kwargs("http://{host}{port}{path}",
                                       {"host": host, "port": port, "path": path})

    def format_es_mapping_url(self, host=None, port=None, route_key=None):
        return self.replace_url_kwargs("http://{host}{port}/{route_key}/_mapping",
                                       {"host": host, "port": port, "route_key": route_key})

    def replace_url_kwargs(self, replace_url, replace_kwargs):
        if not replace_kwargs["host"]:
            replace_kwargs["host"] = self.host
        if not replace_kwargs["port"]:
            replace_kwargs["port"] = self.port
        if replace_kwargs.get("port"):
            replace_kwargs["port"] = f':{replace_kwargs["port"]}'
        else:
            replace_kwargs["port"] = ""
        replace_url = replace_url.format(**replace_kwargs)
        return replace_url

    def close(self):
        pass
