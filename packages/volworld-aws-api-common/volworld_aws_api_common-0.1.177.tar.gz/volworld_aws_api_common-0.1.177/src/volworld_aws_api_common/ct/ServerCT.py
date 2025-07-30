from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.api.url import authUrl
from volworld_common.api.enum.AuthPermission import AuthPermission
from volworld_aws_api_common.test.UserPool import UserPool, UserInfo
from volworld_aws_api_common.test.aws.ATestRequest import ATestRequest
from volworld_aws_api_common.test.api.request_open_api_validation import post_request_with_validation, \
    get_request_with_validation
from volworld_common.api.AuthUser import RootUser
from volworld_common.api.enum.HttpStatus import HttpStatus
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.aws.request.request_util import response_to_dict

class ServerCT:
    def __init__(self):
        self.UserPool = UserPool()
        self.TestRequest = ATestRequest(True)
        self.CurrentLoginToken = None # for root
        self.CurrentLoginUser = None
        self.CurrentUser = None

        self.Resp = None
        self.UrlFeatureDict = dict()
        self.UrlScenarioDict = dict()

        self.AttList = None # Should be assigned
        self.RootUserPassword = None # Should be assigned

    def add_user(self, name: str):
        return self.UserPool.add_user(name)

    def get_user(self, name: str = '') -> UserInfo:
        if name == '':
            return self.CurrentLoginUser
        return self.UserPool.get_user(name)

    def get_token(self, token: str = '') -> str:
        if token != '':
            return token
        if self.CurrentLoginToken is None:
            return self.CurrentLoginUser.token
        return self.CurrentLoginToken

    def do_POST_request_with_validation(self, context, url: str, json, token: str = ''):
        resp_json, resp = post_request_with_validation(
            url, json, self.TestRequest, self.AttList, self.get_token(token)
        )
        resp = response_to_dict(resp_json, resp)
        return self.add_url_test(context, url, resp)

    def do_GET_request_with_validation(self, context, url: str, params = None, token: str = ''):
        resp_json, resp = get_request_with_validation(
            url, self.TestRequest, self.AttList,
            params, self.get_token(token)
        )
        resp = response_to_dict(resp_json, resp)
        return self.add_url_test(context, url, resp)

    def signup(self, name: str) -> UserInfo:
        user = self.add_user(name)
        resp_json, resp = post_request_with_validation(
            authUrl.do_signup_url(), {
                AA.Name: user.used_name,
                AA.Password: user.password,
            }, self.TestRequest, self.AttList
        )
        resp = response_to_dict(resp_json, resp) #post__signup__api_check(user.used_name, user.password, ATestRequest(True))
        assert resp[AA.HttpStatus] == HttpStatus.Created_201.value, resp
        return user

    def login(self, context, name: str) -> UserInfo:
        user = self.get_user(name)
        resp_json, resp = post_request_with_validation(
            authUrl.do_login_url(), {
                AA.Name: user.used_name,
                AA.Password: user.password,
            }, self.TestRequest, self.AttList
        )
        resp = response_to_dict(resp_json, resp)
        assert resp[AA.HttpStatus] == HttpStatus.Ok_200.value
        user.token = resp[AA.Data][AA.Token]
        self.CurrentLoginToken = user.token
        self.CurrentLoginUser = user
        return user

    def login_as_root(self, context):
        resp = self.do_POST_request_with_validation(
            context,
            authUrl.do_login_url(), {
                AA.Name: RootUser.NAME,
                AA.Password: self.RootUserPassword,
            }
        )
        assert resp[AA.HttpStatus] == HttpStatus.Ok_200.value
        self.CurrentLoginToken = resp[AA.Data][AA.Token]
        self.CurrentLoginUser = None

    def get_auth_info(self, context, name: str = ''):
        user: UserInfo = self.CurrentLoginUser
        if name != '':
            user = self.get_user(name)
        assert user.token is not None
        resp = self.do_GET_request_with_validation(
            context,
            authUrl.read_auth_info_url()
        )
        user.uuid = resp[AA.Data][AA.UserUuid]
        return resp[AA.Data]

    def get_permission(self, context, name: str = '') -> AuthPermission:
        info = self.get_auth_info(context, name)
        return AuthPermission(info[AA.Permission])

    def post__update_permission(
            self, context,
            useruuid: str, permission: AuthPermission

    ):
        resp = self.do_POST_request_with_validation(
            context,
            authUrl.update_permission_url(), {
                AA.UserUuid: useruuid,
                AA.Permission: permission.value,
            }
        )

        return resp

    def root_update_current_login_user_permission(self, context, permission: str):
        permission = BehaveUtil.clear_string(permission)
        user: UserInfo = self.CurrentLoginUser
        assert user is not None
        info = self.get_auth_info(context, user.name)
        self.login_as_root(context)
        assert user.uuid is not None, 'use Permission of user {name} is {permission} to get uuid'
        new_permission: AuthPermission = AuthPermission[permission]

        resp = self.post__update_permission(context, user.uuid, new_permission)
        self.Resp = resp
        assert AA.___Error___ not in resp[AA.Data]

        self.login(context, user.name)

    def assert_ok_200_resp(self, resp):
        assert resp[AA.HttpStatus] == HttpStatus.Ok_200.value
        self.Resp = resp

    def add_id_to_url_test_dict(self, url: str, resp, url_dict: dict, id: str):
        if url not in url_dict.keys():
            url_dict[url] = dict()
        status = resp[AA.HttpStatus]
        if status not in url_dict[url].keys():
            url_dict[url][status] = list()
        if id not in url_dict[url][status]:
            url_dict[url][status].append(id)

    def add_url_test(self, context, url: str, resp: any) -> any:
        feature_name = context.feature.name
        scenario_name = context.scenario.name
        feature_id = feature_name.split("]")[0].split("[")[1]
        scenario_id = scenario_name.split("]")[0].split("[")[1]
        print(f"Running Feature: {feature_name} -> {feature_id}")
        print(f"Running Scenario: {scenario_name} -> {scenario_id}")
        self.add_id_to_url_test_dict(url, resp, self.UrlFeatureDict, feature_id)
        self.add_id_to_url_test_dict(url, resp, self.UrlScenarioDict, scenario_id)

        return resp

