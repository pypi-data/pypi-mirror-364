# -*- coding: utf-8 -*-


class StatusCode:
    """
    StatusCode 统一请求返回状态码
    # A表示错误来源于用户，比如参数错误，用户安装版本过低，用户支付超时等问题；
    # B表示错误来源于当前系统，往往是业务逻辑出错，或程序健壮性差等问题；
    # C表示错误来源于第三方服务
    """

    def __init__(self, message=None):
        self.message = message

    # *响应服务请求的状态码与说明

    # 通用状态码
    SUCCESS = ("00000", "请求成功")
    FAIL = ("99999", "请求失败")
    # A00开头的状态码
    USER_VALIDATE_FAIL = ("A0001", "用户端错误")
    # A01开头的状态码
    USER_REGISTER_FAIL = ("A0100", "用户注册错误")
    USER_NAME_VALIDATE_FAIL = ("A0110", "用户名校验失败")
    USER_NAME_EXIST = ("A0111", "用户名已存在")
    USER_NAME_INVALID = ("A0112", "用户名包含特殊字符")
    PHONE_ALREADY_REGISTER = ("A0113", "手机号已经注册")
    PASSWORD_VALIDATE_FAIL = ("A0120", "密码错误")
    PASSWORD_LENGTH_VALID = ("A0121", "密码长度不够")
    SHORT_MESSAGE_VALID_FAIL = ("A0130", "短信验证码错误")
    VALIDATE_CODE_ERROR = ("A0131", "验证码错误！")
    # A02开头的状态码
    USER_LOGIN_EXCEPTION = ("A0200", "用户登录异常")
    USER_ACCOUNT_NOT_EXIST = ("A0201", "用户不存在")
    USER_ACCOUNT_EXPIRE = ("A0202", "账号已失效，请联系管理员！")
    USER_ACCOUNT_PASSWORD_EXPIRE = ("A0203", "密码已失效，请修改密码，重新登录")
    USER_ACCOUNT_EXCEEDED_ERRORS = ("A0204", "密码错误次数过多，账号已锁定，请稍后重试")
    USER_ACCOUNT_DORMANCY = ("A0205", "账号处于休眠状态，请联系管理员！")
    USER_NOT_LOGIN_IN = ("A0206", "用户未登录")
    USER_ROLE_EXPIRE = ("A0207", "账号角色已失效，请联系管理员！")
    # A03开头的状态码
    REQUEST_PARAM_ERROR = ("A0300", "用户请求参数错误")
    INVALID_USER_INPUT = ("A0301", "无效的用户输入")
    INSECURE_TRANSPORT_ERROR = ("A0302", "OAuth 2 必须使用 https.")
    INVALID_REQUEST_ERROR = ("A0303", "无效的请求")
    INVALID_CLIENT_ERROR = ("A0304", "无效客户端信息")
    INVALID_GRANT_ERROR = ("A0305", "无效授权类型")
    UNAUTHORIZED_CLIENT_ERROR = ("A0306", "未授权客户端信息")
    UNSUPPORTED_RESPONSE_TYPE_ERROR = ("A0307", "不支持的响应类型")
    UNSUPPORTED_GRANT_TYPE_ERROR = ("A0308", "不支持的授权类型")
    INVALID_SCOPE_ERROR = ("A0309", "请求的作用域无效、未知或格式不正确")
    ACCESS_DENIED_ERROR = ("A0310", "请求被拒绝")
    MISSING_AUTHORIZATION_ERROR = ("A0311", "请求HEADERS中缺少 AUTHORIZATION 参数")
    UNSUPPORTED_TOKEN_TYPE_ERROR = ("A0312", "不支持的TOKEN类型")
    MISSING_CODE_EXCEPTION = ("A0313", '请求响应中缺少 "CODE"')
    MISSING_TOKEN_EXCEPTION = ("A0314", '请求响应中缺少 "ACCESS_TOKEN"')
    MISSING_TOKEN_TYPE_EXCEPTION = ("A0315", '请求响应中缺少 "TOKEN_TYPE"')
    MISMATCHING_STATE_EXCEPTION = ("A0316", "CSRF告警！请求和响应中的状态不相等")
    INVALID_TOKEN = ("A0317", "token已失效")
    FREQUENCY_LIMIT = ("A0318", "请求次数超限")
    WEIXIN_UNBOUND = ("A0319", "微信未绑定")
    WEIXIN_BOUNDED = ("A0320", "微信已绑定")
    INVALID_TIME_STAMP = ("A0321", "非法的时间戳参数")
    USER_INPUT_INVALID = ("A0322", "用户输入内容非法")
    UNSUPPORTED_SERVICE_TYPE_ERROR = ("A0323", "不支持的服务类型")
    FEISHU_UNBOUND = ("A0324", "飞书未绑定")
    FEISHU_BOUNDED = ("A0325", "飞书已绑定")
    WEIXIN_BOUNDED_OTHER = ("A0326", "微信已绑定在其他帐号了")
    FEISHU_BOUNDED_OTHER = ("A0327", "飞书已绑定在其他帐号了")
    IS_ENTERPRISE_ACCOUNT = ("A0328", "当前帐号是企业帐号")
    NOT_ENTERPRISE_ACCOUNT = ("A0329", "当前帐号不是企业帐号")
    INVALID_ONLY_TOKEN = ("A0330", "单设备登录的token已失效")
    INVALID_REFRESH_TOKEN = ("A0331", "无效的REFRESH_TOKEN")
    INSUFFICIENT_THIRD_PERMISSION = ("A0332", "三方权限不足")
    INSUFFICIENT_OPERATION_PERMISSION = ("A0333", "操作权限不足")
    INVALID_FILE_PARAMETERS = ("A0334", "无效的文件参数")
    FILE_STORAGE_EXCEPTION = ("A0335", "文件存储异常")
    DATABASE_CONNECT_EXCEPTION = ("A0336", "数据库连接异常")
    UNABLE_OBTAIN_PHONE = ("A0340", "无法获取到手机号")
    UNAUTHORIZED_USER = ("A0341", "没有找到授权的用户")
    DATA_ERROR = ("A0342", "数据有误")

    @staticmethod
    def MONITOR_EXCEPTION(message):
        """
        监控异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0390", "监控异常:{}".format(message)

    @staticmethod
    def SEVICE_EXCEPTION(message):
        """
        服务调用异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0391", "服务调用异常:{}".format(message)

    @staticmethod
    def MESSAGE_QUEUE_EXCEPTION(message):
        """
        消息队列异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0392", "消息队列异常:{}".format(message)

    @staticmethod
    def REQUEST_HEADER_EXCEPTION(message):
        """
        请求头异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0393", "请求头异常:{}".format(message)

    @staticmethod
    def CHART_EXCEPTION(message):
        """
        图表异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0394", "图表异常:{}".format(message)

    @staticmethod
    def ENCRYPTION_EXCEPTION(message):
        """
        加密异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0395", "加密异常:{}".format(message)

    @staticmethod
    def TASK_EXCEPTION(message):
        """
        任务异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0396", "任务异常:{}".format(message)

    @staticmethod
    def DATABASE_FIELD_EXCEPTION(message):
        """
        数据库字段异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0397", "数据库字段异常:{}".format(message)

    @staticmethod
    def ThirdServiceError(message):
        """
        调用第三方接口失败
        :param message: 替换的消息内容
        :return:
        """
        return "A0398", "调用第三方接口失败:{}".format(message)

    @staticmethod
    def REQUIRED_PARAM_IS_EMPTY(message):
        """
        请求参数异常
        :param message: 替换的消息内容
        :return:
        """
        return "A0399", "请求缺少必要参数:{}".format(message)

    # A04开头的状态码
    VALIDATE_CODE_EXPIRE = ("A0400", "验证码过期")
    FORM_VALIDATE_FAIL = ("A0401", "表单校验失败")
    PARAM_VALIDATE_FAIL = ("A0402", "参数校验失败")
    PARAM_BIND_FAIL = ("A0403", "参数绑定失败")
    PHONE_NUM_NOT_FOUND = ("A0404", "找不到该用户，手机号码有误")

    # A40开头的状态码
    REQUEST_PATH_NOT_FOUND = ("A4041", "请求地址不存在")

    # A05开头的状态码

    # B00开头的状态码
    @staticmethod
    def BUSINESS_FAIL(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0000", "{}".format(message)

    ACCESS_DENIED = ("B0001", "访问权限不足")
    RESOURCE_DISABLED = ("B0002", "资源被禁用")
    RESOURCE_NO_AUTHORITY = ("B0003", "该资源未定义访问权限")

    # B01开头的状态码
    TIMEOUT = ("B0100", "系统执行超时")
    TASK_PENDING = ("B0101", "任务等待中")
    TASK_RUNNING = ("B0102", "任务运行中")
    TASK_SUCCESS = ("B0103", "任务成功")
    TASK_FAIL = ("B0104", "任务失败")
    TASK_NOT_EXIST = ("B0105", "任务不存在")
    COMPANY_CERTIFICATION_FAIL = ("B0106", "企业认证失败")
    IDENTITY_CERTIFICATION_FAIL = ("B0107", "身份证认证失败")
    COMPANY_CERTIFICATION_OTHER = ("B0108", "企业已经被认证")
    IDENTITY_CERTIFICATION_OTHER = ("B0109", "身份证已认证")
    COMPANY_CERTIFICATION_PENDING = ("B0110", "企业正在认证")
    IDENTITY_CERTIFICATION_PENDING = ("B0111", "身份证正在认证")
    COMPANY_NOT_CERTIFICATION = ("B0112", "企业未认证")
    IDENTITY_NOT_CERTIFICATION = ("B0113", "身份证未认证")
    # B02开头的状态码
    STRIKE_RECOVERY = ("B0200", "系统容灾系统被触发")
    # B03开头的状态码
    UNSUPPORTED_REQUEST_TYPE = ("B0301", "不支持的请求类型")

    # B04开头的状态码
    RESOURCE_NOT_FOUND = ("B0404", "访问资源不存在")

    @staticmethod
    def RESOURCE_NOT_EXIST(resource):
        return "B0405", f"访问资源({resource})不存在"

    @staticmethod
    def BOUNDED(info):
        return "B0406", f"三方账号({info})已绑定其他账号"

    @staticmethod
    def UNBOUNDED(info):
        return "B0407", f"三方账号({info})还没有绑定"

    # B05开头的状态码
    @staticmethod
    def INTERNAL_SERVER_ERROR(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0500", "服务器内部错误:{}".format(message)

    @staticmethod
    def RESOURCE_EXIST(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0501", "{}已存在,确保唯一性，不可重复".format(message)

    @staticmethod
    def RESOURCE_NOT_EXIST(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0502", "{}".format(message)

    # C00开头的状态码
    RPC_INVOKE_ERROR = ("C0001", "调用第三方服务出错")
    SERVER_ERROR = ("C0002", "服务器内部错误")
    UNKNOWN_ERROR = ("C0003", "未知异常")

    # C01开头的状态码

    # C02开头的状态码

    # C03开头的状态码

    # C04开头的状态码

    # C05开头的状态码
    @staticmethod
    def AT_LEAST_ONE_NOT_EMPYT(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "C0502", "{}至少存在一个不为空".format(message)

    @staticmethod
    def COMMON_CODE_MESSAGE(status_code, message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return status_code, "{}".format(message)
