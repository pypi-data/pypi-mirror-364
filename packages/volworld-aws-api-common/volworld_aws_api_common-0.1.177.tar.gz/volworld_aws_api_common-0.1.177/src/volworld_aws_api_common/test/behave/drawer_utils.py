
import time

from selenium.webdriver.remote.webelement import WebElement
from volworld_common.api.CA import CA

from volworld_aws_api_common.api.dom_id import dom_id
from volworld_aws_api_common.test.behave.selenium_utils import w__click_element_by_dom_id, get_element_by_dom_id


def waiting_for_drawer_animation():
    time.sleep(0.2)


def click_to_open_list_nav_drawer(c, tar_id: str, prefix=None) -> WebElement:
    if prefix is None:
        prefix = list()
    elm = w__click_element_by_dom_id(c, prefix + [CA.List, CA.Navigator, tar_id, CA.Button])

    waiting_for_drawer_animation()
    return elm


def click_to_close_list_nav_drawer(c, tar_id: str, prefix=None) -> WebElement:
    if prefix is None:
        prefix = list()
    dom_id_list = prefix + [tar_id, CA.Drawer, CA.Header, CA.Close, CA.Button]
    elm = get_element_by_dom_id(c, dom_id_list)
    if elm is None:
        print(f"Can NOT find close button of id=[{dom_id(dom_id_list)}]")
        return None

    elm = w__click_element_by_dom_id(c, dom_id_list)

    waiting_for_drawer_animation()
    return elm