import inspect
from typing import List, Dict

swagger_json_project = []

swagger_json_class = []
python_column_type_dict = {
    "list": "array",
    "str": "string",
    "int": "integer",
    "dict": "object",
    "bool": "boolean",
    "float": "multipleOf"
}
definitions = {}


def parser_swagger(func, desc):
    if type(func).__name__ == "type":
        swagger_json_project.append(
            {
                "desc": desc,
                "route": func.__route_name__,
                "method_list": swagger_json_class.copy()
            }
        )
        swagger_json_class.clear()

    elif type(func).__name__ == "function":
        param_list = [{
            "name": "Authorization",
            "in": "header",
            "required": False,
            "type": "string"
        }, {
            "name": "User",
            "in": "header",
            "required": False,
            "type": "string"
        }]
        args = get_args(func)
        if func.__http_method__ == "get":
            param_list.extend(args)
            swagger_json_class.append({
                "route": func.__route_name__,
                "summary": "Place an order for a pet",
                "introduce": func.__doc__,
                "operationId": "placeOrder",
                "consumes": ["application/json"],
                "produces": ["application/json", "application/xml"],
                "parameters": param_list,
                "description": desc,
                "http_method": func.__http_method__
            })
        elif func.__http_method__ == "post":
            schema = {
                "type": "object",
                "properties": {
                }
            }
            for param in args:
                param_type = param.get("type")
                if param_type in ["integer", "string"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": param_type,
                        "enum": [param.get("default", "string")]
                    }
                elif param_type in ["array"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "array",
                        "xml": {"wrapped": True},
                        "items": {"type": "string"},
                        "enum": [param.get("default", "string")]
                    }
                elif param_type in ["object"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "object",
                        "properties": {

                        }
                    }
                elif param_type == "boolean":
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "boolean"
                    }
                if "default" in param:
                    schema["properties"][param.get("name", "")]["default"] = param.get("default", "")
            param_list.append({
                "required": True,
                "name": "body",
                "in": "body",
                "schema": schema
            })
            swagger_json_class.append({
                "route": func.__route_name__,
                "parameters": param_list,
                "description": desc,
                "http_method": func.__http_method__,
                "introduce": func.__doc__
            })
        else:
            schema = {
                "type": "object",
                "properties": {
                }
            }
            for param in args:
                param_type = param.get("type")
                if param_type in ["integer", "string"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": param_type,
                        "enum": [param.get("default", "string")]
                    }
                elif param_type in ["array"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "array",
                        "xml": {"wrapped": True},
                        "items": {"type": "string"},
                        "enum": [param.get("default", "string")]
                    }
                elif param_type in ["object"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "object",
                        "properties": {

                        }
                    }
                elif param_type in ["boolean"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "boolean",
                        "properties": {

                        }
                    }
                elif param_type in ["number"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "number",
                        "properties": {

                        }
                    }
                if "default" in param:
                    schema["properties"][param.get("name", "")]["default"] = param.get("default", "")
            param_list.append({
                "required": True,
                "name": "body",
                "in": "body",
                "schema": schema
            })
            swagger_json_class.append({
                "route": func.__route_name__,
                "parameters": param_list,
                "description": desc,
                "http_method": func.__http_method__,
                "introduce": func.__doc__
            })


def get_args(func):
    params_list = []
    signature = inspect.signature(func)
    for parameter_name, parameter in signature.parameters.items():
        if parameter_name == 'self':
            continue
        else:
            item_type = None
            parameter_type = parameter.annotation
            if parameter_type is inspect.Parameter.empty:
                parameter_type = type(parameter.default)
            parameter_default = None
            if parameter.default is not inspect.Parameter.empty:
                parameter_default = parameter.default
            if parameter_type == int:
                parameter_type_str = "integer"
            elif parameter_type == str:
                parameter_type_str = "string"
            elif parameter_type in [list, tuple, set, List, List[Dict], List[str],
                                    List[int], List[float], List[bool], List[dict]]:
                parameter_type_str = "array"
                if parameter_type in [List[Dict], List[dict]]:
                    item_type = "object"
                elif parameter_type in [List[int], List[float]]:
                    item_type = "number"
                elif parameter_type == List[bool]:
                    item_type = "boolean"
                else:
                    item_type = "string"
            elif parameter_type == float:
                parameter_type_str = "number"
            elif parameter_type == bool:
                parameter_type_str = "boolean"
            else:
                parameter_type_str = "object"
            params = {
                "required": False if parameter.default is not inspect.Parameter.empty else True,
                "name": parameter_name,
                "in": "query",
                "type": parameter_type_str,
                "default": parameter_default
            }
            if item_type:
                params.update({"items": {"type": item_type}})
            params_list.append(params)
    return params_list
