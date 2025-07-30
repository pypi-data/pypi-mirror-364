from requests import Response
from volworld_common.test.Timer import Timer
from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.api.ApiUrl import ApiUrl
from volworld_aws_api_common.test.aws.ATestRequest import ATestRequest
from volworld_aws_api_common.test.request import post_request, get_request
from volworld_aws_api_common.api.enum.ErrorCode import ErrorCode
from volworld_aws_api_common.api.enum.HttpStatus import HttpStatus

from volworld_aws_api_common.test.api.OpenApiValidation import OpenApiValidation
import json

def request_open_api_post_validation(url: str, req, resp_json, resp: Response, attList, api_yaml_file: str=None):
    url = url.replace(ApiUrl.Root, '')
    url = url.replace('//', '/')
    if not url.startswith('/'):
        url = f"/{url}"

    val = OpenApiValidation(api_yaml_file)
    val.validate_POST_request(req, url, attList)

    print("[db_fn_open_api_validation] res JSON = ",  json.dumps(resp_json))
    print("[db_fn_open_api_validation] resp.status_code = ", resp.status_code)
    if AA.___Error___ not in resp_json:
        if 'message' in resp_json:
            if resp_json['message'] == 'Invalid request body':
                val.validate_POST_response({
                    AA.___Error___:  'Invalid request body'
                }, url, HttpStatus.Bad_Request_400, attList)
                return
        val.validate_POST_response({
            AA.Data: resp_json[AA.Data]
        }, url, resp.status_code, attList)
    else:
        val.validate_POST_response({
            AA.___Error___: resp_json[AA.___Error___]
        }, url, resp.status_code, attList)


def request_open_api_get_validation(url: str, resp_json, resp: Response, attList, api_yaml_file: str =None):
    url = url.replace(ApiUrl.Root, '')
    url = url.replace('//', '/')
    if not url.startswith('/'):
        url = f"/{url}"

    val = OpenApiValidation(api_yaml_file)

    print("[db_fn_open_api_validation] resp JSON = ",  json.dumps(resp_json))
    print("[db_fn_open_api_validation] resp.status_code = ", resp.status_code)
    if AA.___Error___ not in resp_json:
        if 'message' in resp_json:
            if resp_json['message'] == 'Invalid request body':
                val.validate_GET_response({
                    AA.___Error___:  'Invalid request body'
                }, url, HttpStatus.Bad_Request_400, attList)
                return
        val.validate_GET_response({
            AA.Data: resp_json[AA.Data]
        }, url, resp.status_code, attList)
    else:
        val.validate_GET_response({
            AA.___Error___: resp_json[AA.___Error___]
        }, url, resp.status_code, attList)

def post_request_with_validation(
        url: str, req: dict,
        test_req: ATestRequest, attList,
        token: str = None,
        api_yaml_file: str = None):
    with Timer(f"Call DB Function [{url}]"):
        resp_json, resp = post_request(url, req, test_req, attList, token=token)
    request_open_api_post_validation(url, req, resp_json, resp, attList, api_yaml_file=api_yaml_file)
    return resp_json, resp

def get_request_with_validation(
        url: str,
        test_req: ATestRequest, attList,
        params: dict = None,
        token: str = None,
        api_yaml_file: str = None):
    with Timer(f"Call DB Function [{url}]"):
        resp_json, resp = get_request(url, test_req, attList, params=params, token=token)
    request_open_api_get_validation(url, resp_json, resp, attList, api_yaml_file=api_yaml_file)
    return resp_json, resp