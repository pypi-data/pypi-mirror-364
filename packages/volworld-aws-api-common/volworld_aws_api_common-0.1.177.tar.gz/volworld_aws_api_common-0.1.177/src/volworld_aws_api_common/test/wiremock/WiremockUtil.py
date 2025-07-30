import json
import requests
from volworld_common.test.behave.BehaveUtil import BehaveUtil


class WiremockUtil:

    @staticmethod
    def rest_all_scenario(root_url: str):
        url = f"{root_url}/__admin/scenarios/reset"
        print(f"post_url = {url}")
        resp = requests.post(url, {})
        print(f"reset mock = {resp.text}")

    @staticmethod
    def set_mock_state(root_url: str, url: str, state: str):
        state = BehaveUtil.clear_string(state).lower()
        WiremockUtil.rest_all_scenario(root_url)
        url = f"{root_url}/{url}/{state}"
        print(f"post url = {url}")
        resp = requests.post(url, {})
        print(f"set mock = {resp.text}")

    @staticmethod
    def set_scenario_state(root_url: str, scenario: str, state: str):
        scenario = BehaveUtil.clear_string(scenario).lower()
        state = BehaveUtil.clear_string(state)
        url = f"{root_url}/__admin/scenarios/{scenario}/state"
        data = json.dumps({"state": state})
        print(f"put_url = {url}")
        print(f"data = {data}")
        resp = requests.put(url, data)
        print(f"set mock = {resp.text}")