

from volworld_aws_api_common.test.wiremock.WiremockUtil import WiremockUtil


class Wiremock:

    ROOT_URL = f"http://localhost:00000"

    @staticmethod
    def rest_all_scenario():
        WiremockUtil.rest_all_scenario(Wiremock.ROOT_URL)
        # WiremockUtil.rest_all_scenario(Wiremock.ROOT_URL)

    @staticmethod
    def set_mock_state(url: str, state: str):
        WiremockUtil.set_mock_state(Wiremock.ROOT_URL, url, state)
        # WiremockUtil.set_mock_state(Wiremock.ROOT_URL, url, state)

    @staticmethod
    def set_scenario_state(scenario: str, state: str):
        WiremockUtil.set_scenario_state(Wiremock.ROOT_URL, scenario, state)