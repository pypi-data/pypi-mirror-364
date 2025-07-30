from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.api.Aws import Aws


def response_to_dict(resp_json, resp) -> dict:
    data = None
    error = None

    if Aws.Message in resp_json.keys():
        error = resp_json[Aws.Message]
    elif AA.___Error___ in resp_json.keys():
        error = resp_json[AA.___Error___]
    else:
        data = resp_json[AA.Data]

    return {
            AA.Data: data,
            AA.___Error___: error,
            AA.HttpStatus: resp.status_code,
            AA.Response: resp
        }