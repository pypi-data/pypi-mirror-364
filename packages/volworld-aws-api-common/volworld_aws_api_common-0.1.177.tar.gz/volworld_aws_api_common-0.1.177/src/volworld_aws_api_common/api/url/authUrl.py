from typing import Final

from volworld_aws_api_common.api.AA import AA

from volworld_aws_api_common.test.aws.url import build_api_root_url
from volworld_aws_api_common.test.aws.url import build_url
from volworld_aws_api_common.test.aws.url import build_dynamic_url

# ROOT__: Final[str] = build_api_root_url(AA.Auth)
#
# doSignupUrl: Final[str] = build_url(ROOT__, AA.Signup)
#
# doLoginUrl: Final[str] = build_url(ROOT__, AA.Login)
#
# # doLogoutUrl: Final[str] = build_url(ROOT__, AA.Logout)
#
# currentUserUrl: Final[str] = build_url(ROOT__, AA.UserId)


ROOT__: Final[list] = [AA.Auth]

def do_signup_url():
    return build_dynamic_url(ROOT__, [AA.Signup])

def do_login_url():
    return build_dynamic_url(ROOT__, [AA.Login])

def read_auth_info_url():
    return build_dynamic_url(ROOT__, [AA.Info])

def update_permission_url():
    return build_dynamic_url(ROOT__, [AA.Update, AA.Permission])

def current_user_url():
    return build_dynamic_url(ROOT__, [AA.UserId])

