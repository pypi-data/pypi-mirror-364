import json
import requests
from requests import Response

from volworld_common.api import CA
from volworld_common.test.Timer import Timer
from volworld_common.util.json import print_json_by_attributes

from volworld_aws_api_common.test.aws.ATestRequest import ATestRequest

APP_HEADER = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json',
    'Accept-Encoding': 'deflate, gzip'}


def auth_header(token: str):
    return {
        # 'Authorization': token,  # self.token_type_ + " " + self.token_,
        # 'AuthorizeToken': token,
        'Authorization': f"Bearer {token}",
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate'
    }


# def print_json(j, print_long_att: bool = False):
#     if not print_long_att:
#         print(json.dumps(j, indent=4, sort_keys=True))
#         return
#
#     abb_att = dict()
#     for name in CA.__dict__:
#         abb = CA.__dict__[name]
#         abb_att[f"\"{abb}\":"] = f"\"{abb}__{name}\":"
#     res = json.dumps(j, indent=4, sort_keys=True)
#     for att in abb_att.keys():
#         res = res.replace(att, abb_att[att])
#     print(res)


def post_url(url: str, post_j: dict, attList,
             print_url_params: bool = True,
             print_long_att: bool = True,
             # status_code: int = -1,
             headers: dict = None) -> (dict, Response):
    print('[post_url] print_long_att = ', print_long_att)
    if headers is None:
        headers = APP_HEADER
    if print_url_params:
        print(f'==== [Url] [{url}] ====')
        print('=== POST ===')
        print('<code>')
        print_json_by_attributes(post_j, attList, print_long_att)
        print('</code>')
    session = requests.Session()
    print('[post_url] session = ', session.cookies.get_dict())
    print('[post_url] req headers = ', headers)
    resp = requests.post(url, headers=headers, json=post_j)
    print(f'[post_url] resp headers = {resp.headers}')
    print(f'[post_url] resp = {resp.text}')
    resp_json = resp.json()
    if print_url_params:
        print('=== Response ===')
        print('<code>')
        print_json_by_attributes(resp_json, attList, print_long_att)
        print('</code>')
    # if status_code > 0:
    #     assert(resp.status_code == status_code), resp.status_code
    print('[post_url] session.cookies = ', session.cookies.get_dict())
    return resp_json, resp


def post_request(
        url: str,
        post_j: dict,
        req: ATestRequest,
        attList,
        token: str = None) -> (dict, Response):
    headers = None
    if token is not None:
        headers = auth_header(token)
    with Timer(url):
        return post_url(url, post_j, attList,
                        print_url_params=req.print_url_params,
                        print_long_att=req.print_long_att,
                        # status_code=status_code,
                        headers=headers)


def get_url(url: str, attList, params=None, cookies: dict = None,
            print_url_params: bool = True,
            print_long_att: bool = True,
            headers: dict = None) -> (dict, Response):
    if headers is None:
        headers = APP_HEADER
    if params is None:
        params = dict()
    if print_url_params:
        print(f'==== [Url] [{url}] ====')
        print('=== GET ===')
        print('<code>')
        print_json_by_attributes(params, attList, print_long_att)
        print('</code>')
    session = requests.Session()
    print('[get_url] session = ', session.cookies.get_dict())
    print('[get_url] cookies = ', cookies)

    resp = requests.get(url, headers=headers, params=params, cookies=cookies)
    print(f'[get_url] resp headers = {resp.headers}')
    print(f'[get_url] resp = {resp.text}')
    resp_json = resp.json()
    if print_url_params:
        print('=== Response ===')
        print('<code>')
        print_json_by_attributes(resp_json, attList, print_long_att)
        print('</code>')
    # if status_code > 0:
    #     assert(resp.status_code == status_code), resp.status_code
    print('[get_url] session = ', session.cookies.get_dict())
    return resp_json, resp


def get_request(
        url: str,
        req: ATestRequest,
        attList,
        params: dict = None,
        cookies: dict = None,
        token: str = None) -> (dict, Response):
    headers = None
    if token is not None:
        headers = auth_header(token)
    with Timer(url):
        if params is None:
            params = dict()
        return get_url(url, attList, params, cookies,
                       print_url_params=req.print_url_params,
                       print_long_att=req.print_long_att,
                       headers=headers)
