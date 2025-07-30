
from volworld_aws_api_common.test.behave.selenium_utils import get_element_by_dom_id


def assert_input_elm_enabled_by_dom_id(c, ids: list, enabled: bool):
    elm = get_element_by_dom_id(c, ids)
    # print(f"innerHtml = {elm.get_attribute('outerHTML')}")
    disabled = elm.get_attribute("disabled")
    if enabled:
        assert disabled is None
    else:
        assert enabled == (not elm.get_attribute("disabled")), \
            f"enabled = {enabled} != {elm.is_enabled()} = elm = {elm.get_attribute('disabled')} = disabled"


def assert_input_elm_selected_by_dom_id(c, ids: list):
    elm = get_element_by_dom_id(c, ids)
    assert elm.is_selected()


def assert_input_elm_not_selected_by_dom_id(c, ids: list):
    elm = get_element_by_dom_id(c, ids)
    assert not elm.is_selected()