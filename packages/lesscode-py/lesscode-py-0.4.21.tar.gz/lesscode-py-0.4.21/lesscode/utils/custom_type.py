class User:
    """
    用户对象类
    """

    def __init__(self):
        # '账号id',
        self.id = None
        # 用户名
        self.username = None
        # '密码',
        self.password = None
        # '显示名',
        self.display_name = None
        # 手机号,
        self.phone_no = None
        #  邮箱
        self.email = None
        # 组织机构id',
        self.org_id = None
        # '1正常（激活）；2未激活（管理员新增，首次登录需要改密码）； 3锁定（登录错误次数超限，锁定时长可配置）； 4休眠（长期未登录（字段，时长可配置），定时） 5禁用-账号失效；
        self.account_status = None
        # 角色id集合
        self.roleIds = None

    def __str__(self):
        return (f"User(id={self.id},username={self.username},phone_no={self.phone_no},"
                f"display_name={self.display_name},email={self.email},org_id={self.org_id},"
                f"account_status={self.account_status},roleIds={self.roleIds})")

    def __repr__(self):
        return (f"User(id={self.id},username={self.username},phone_no={self.phone_no},"
                f"display_name={self.display_name},email={self.email},org_id={self.org_id},"
                f"account_status={self.account_status},roleIds={self.roleIds})")
