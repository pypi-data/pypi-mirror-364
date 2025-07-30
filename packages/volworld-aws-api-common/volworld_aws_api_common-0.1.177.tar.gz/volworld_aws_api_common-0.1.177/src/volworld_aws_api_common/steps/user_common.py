from behave import *
from volworld_common.test.behave.BehaveUtil import BehaveUtil
import random
from volworld_aws_api_common.test.behave.ACotA import ACotA


@given('{user}, a guest')
def given__a_guest(context, user: str):
    pass


@given('{mentor}, a signed up login Mentor')
def given__a_mentor(context, mentor: str):
    pass

@given('{learner}, a signed up login Learner')
def given__a_learner(context, learner: str):
    pass


@given('[user name] is rand [{name}]')
def given__rand_user_name(c, name: str):
    name = BehaveUtil.clear_string(name)
    name = f"{name}{random.randint(1000000, 9999999)}"
    setattr(c, ACotA.UserName, name)


@given('[user password] is rand [{password}]')
def given__rand_user_password(c, password: str):
    password = BehaveUtil.clear_string(password)
    password = f"{password}{random.randint(1000000, 9999999)}"
    setattr(c, ACotA.UserPassword, password)