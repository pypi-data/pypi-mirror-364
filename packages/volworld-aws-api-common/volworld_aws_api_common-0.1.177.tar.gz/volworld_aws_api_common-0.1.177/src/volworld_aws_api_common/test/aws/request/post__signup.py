
from volworld_aws_api_common.api.enum.HttpStatus import HttpStatus
from volworld_common.util.id_util import new_rand_test_user_name
from volworld_aws_api_common.api.AA import AA, AAList
from volworld_aws_api_common.api.Aws import Aws
from volworld_aws_api_common.api.url import authUrl
from volworld_aws_api_common.test.aws.ATestRequest import ATestRequest
from volworld_aws_api_common.test.request import post_request
from volworld_aws_api_common.test.aws.request.request_util import response_to_dict


def post__signup(
        name: str, pw: str,
        req: ATestRequest,
        ):
    resp_json, resp = post_request(
        authUrl.do_signup_url(), {
            AA.Name: name,
            AA.Password: pw,
        }, req, AAList
        )
    return response_to_dict(resp_json, resp)


def act__signup(name: str = None, pw: str = None) -> dict:
    if name is None:
        name = new_rand_test_user_name()
    if pw is None:
        pw = 'password'
    resp = post__signup(name, pw, ATestRequest(True))
    if resp[AA.Data] is not None:
        assert resp[AA.HttpStatus] == HttpStatus.Created_201.value
        assert resp[AA.Data][AA.Ok] is True
        resp[AA.Name] = name
        resp[AA.Password] = pw
        return resp
    else:
        assert AA.___Error___ in resp
    return resp
