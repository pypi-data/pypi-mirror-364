from volworld_common.util.id_util import new_rand_test_user_name
from volworld_aws_api_common.test.aws.request.post__signup import act__signup
from volworld_aws_api_common.test.aws.request.post__login import act__login
from volworld_aws_api_common.api.AA import AA
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.behave.ACotA import ACotA
from volworld_aws_api_common.api.enum.ErrorCode import ErrorCode
from typing import Final

DEFAULT_USER_PASSWORD: Final[str] = 'default_password'

class UserInfo:
    def __init__(self, name: str, password: str = DEFAULT_USER_PASSWORD, rand_user: bool = True):
        self.name = name
        # for testing wrong formatted username, put the name before generated id
        subfix = ''
        if rand_user:
            subfix = f"xxx{new_rand_test_user_name()}"
        self.used_name = f"{self.name}{subfix}"
        self.password = password
        self.token = None
        self.login_info = None
        self.uuid = None
        self.titles = []
        self.flags = []

    def signup(self):
        login = act__signup(self.used_name, self.password)
        if login[AA.___Error___] is not None:
            if login[AA.___Error___][AA.Code] == ErrorCode.UserNameExisting:
                print(f"{self.used_name} already exist!")
                return
        assert login[AA.Name] == self.used_name
        self.password = login[AA.Password]

    def login(self, forced=False):
        if not forced and self.login_info is not None:
            return

        print("act__login")
        self.login_info = act__login(self.used_name, self.password)
        print("login_info = ", self.login_info)
        self.token = self.login_info[AA.Token]
        print("set token = ", self.token)
        # print("")
        # print("")
        return self.login_info


class UserPool:
    def __init__(self):
        self.users = dict()

    def get_user(self, name: str) -> UserInfo:
        name = BehaveUtil.clear_string(name)
        if name not in self.users:
            return None

        return self.users[name]

    def get_login_user(self, name: str) -> UserInfo:
        user = self.get_user(name)
        user.login()
        return user

    def add_user(self, name: str, password: str = DEFAULT_USER_PASSWORD, rand_user: bool = True) -> UserInfo:
        name = BehaveUtil.clear_string(name)
        assert name not in self.users
        self.users[name] = UserInfo(name, password, rand_user=rand_user)
        return self.users[name]

    def add_signup_user(self, name: str, password: str = DEFAULT_USER_PASSWORD, rand_user: bool = True) -> UserInfo:
        name = BehaveUtil.clear_string(name)
        assert name not in self.users
        inf = UserInfo(name, password, rand_user=rand_user)
        self.users[name] = inf
        inf.signup()
        return inf

    def login(self, context, name):
        name = BehaveUtil.clear_string(name)
        user: UserInfo = self.users[name]
        assert user is not None
        if hasattr(context, 'curr_login_user'):
            if getattr(context, ACotA.LoginUser) == user:
                return
        curr_login_name = 'None'
        if hasattr(context, ACotA.LoginUser):
            curr_login_name = getattr(context, ACotA.LoginUser).name

        print(f"Need to login [{name}], current login is [{curr_login_name}]")
        user.login()
        setattr(context, ACotA.LoginUser, user)

        return user
