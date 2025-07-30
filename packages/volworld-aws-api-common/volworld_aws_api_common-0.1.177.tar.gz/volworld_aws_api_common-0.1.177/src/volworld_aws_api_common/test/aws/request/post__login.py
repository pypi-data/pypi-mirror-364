from volworld_aws_api_common.api.AA import AA, AAList
from volworld_aws_api_common.api.url import authUrl
from volworld_aws_api_common.test.aws.ATestRequest import ATestRequest
from volworld_aws_api_common.test.request import post_request
from volworld_aws_api_common.test.aws.request.post__signup import act__signup
from volworld_aws_api_common.api.enum.HttpStatus import HttpStatus

from volworld_aws_api_common.api.Aws import Aws
from volworld_aws_api_common.test.aws.request.request_util import response_to_dict


def post__login(
        name: str, pw: str,
        req: ATestRequest,
        # status_code: int = -1
):
    resp_json, resp = post_request(
        authUrl.do_login_url(), {
            AA.Name: name,
            AA.Password: pw,
        }, req, AAList
    )

    return response_to_dict(resp_json, resp)


def act__login(name: str = None, pw: str = None) -> dict:
    resp = post__login(name, pw, ATestRequest(True))
    if resp[AA.Data] is not None:
        assert resp[AA.HttpStatus] == HttpStatus.Ok_200.value
        resp[AA.Token] = resp[AA.Data][AA.Token]
    else:
        assert AA.___Error___ in resp
    return resp


def act__signup_login(name: str = None, pw: str = None) -> dict:
    signup = act__signup(name, pw)
    resp = post__login(signup[AA.Name], signup[AA.Password], ATestRequest(True))
    assert resp[AA.HttpStatus] == HttpStatus.Ok_200.value
    return {
        AA.Name: signup[AA.Name],
        AA.Password: signup[AA.Password],
        AA.Data: resp[AA.Data],
        AA.Token: resp[AA.Data][AA.Token]
    }