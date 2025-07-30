
from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.api.ApiUrl import ApiUrl

# URL_ROOT = "https://958e36p8n5.execute-api.ap-northeast-1.amazonaws.com/prod/"


def build_api_root_url(*elms) -> str:
    es = list()
    for e in elms:
        es.append(e)
    return f"{ApiUrl.Root}/{AA.Api}/{'/'.join(es)}"
    # return URL_ROOT + '/' + '/'.join(es)


def build_url(root, *elms) -> str:
    es = list()
    for e in elms:
        es.append(e)
    return f"{root}/{'/'.join(es)}"
    # return root + '/' + '/'.join(es)


def build_dynamic_url(root: list, path: list):
    root = f"{ApiUrl.Root}{AA.Api}/{'/'.join(root)}"
    return f"{root}/{'-'.join(path)}"