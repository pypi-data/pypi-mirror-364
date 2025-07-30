from behave import *
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.behave.ACotA import ACotA
from volworld_aws_api_common.test.wiremock.Wiremock import Wiremock


def set_mock_scenario(c, scenario: str):
    scenario = BehaveUtil.clear_string(scenario)
    setattr(c, ACotA.MockScenario, scenario)


@given('mock scenario is [{scenario}]')
def given__set_mock_scenario(c, scenario: str):
    set_mock_scenario(c, scenario)


@when('system reset all mock scenario')
def when__system_reset_all_mock_scenario(c):
    Wiremock.rest_all_scenario()


@given('system reset all mock scenario')
def given__system_reset_all_mock_scenario(c):
    Wiremock.rest_all_scenario()


def set_system_mock_state_by_name(c, state: str):
    scenario = getattr(c, ACotA.MockScenario)
    assert scenario == scenario.lower(), f"Scenario [{scenario}] should be lower case."
    assert scenario is not None
    state = BehaveUtil.clear_string(state)
    Wiremock.set_scenario_state(scenario, state)


@when('mock scenario state is [{state}]')
def when__set_system_mock_state_by_name(c, state: str):
    set_system_mock_state_by_name(c, state)


@given('mock scenario state is [{state}]')
def given__set_system_mock_state_by_name(c, state: str):
    set_system_mock_state_by_name(c, state)