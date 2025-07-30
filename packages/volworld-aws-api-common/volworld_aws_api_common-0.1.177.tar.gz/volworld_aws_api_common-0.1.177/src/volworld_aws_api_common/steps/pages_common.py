from behave import *
from selenium.webdriver.common.by import By
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.behave.ACotA import ACotA
from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.test.behave.selenium_utils import w__click_element_by_dom_id, \
    w__get_element_by_shown_dom_id, w__assert_element_not_existing, w__assert_element_existing, click_element


def set_target_page(c, target_page: str):
    target_page = BehaveUtil.clear_string(target_page)
    setattr(c, ACotA.TargetPage, target_page)


@given('target page is [{target_page}]')
def given__set_target_page(c, target_page: str):
    set_target_page(c, target_page)


@when('target page is [{target_page}]')
def when__set_target_page(c, target_page: str):
    set_target_page(c, target_page)



@then('the current page showing in page list bar is {page_str}')
def then__the_current_page_showing_in_page_controller(c, page_str: str):
    elm = w__get_element_by_shown_dom_id(c, [AA.Page, BehaveUtil.clear_string(page_str), AA.Button])
    assert elm.get_attribute("data-btn-info") == "curr"

    # class_list = elm.get_attribute("class").split()
    # found_curr_class = False
    # for c in class_list:
    #     if c.find('StPagination_CurrButton') > -1:
    #         found_curr_class = True
    #         break
    # assert found_curr_class


@then('[previous page button] is NOT showing in bottom app bar')
def then__previous_page_button_is_not_showing_in_bottom_app_bar(c):
    w__assert_element_not_existing(c, [AA.BottomAppBar, AA.PreviousPage, AA.Button])


@then('[previous page button] is showing in bottom app bar')
def check_previous_page_btn_showing(c):
    # elm = w__get_element_by_shown_dom_id(c, [AA.BottomAppBar, AA.Add, AA.Book, AA.Button])
    w__assert_element_existing(c, [AA.BottomAppBar, AA.PreviousPage, AA.Button])


@then('[next page button] is NOT showing in bottom app bar')
def then__next_page_button_is_not_showing_in_bottom_app_bar(c):
    # elm = w__get_element_by_shown_dom_id(c, [AA.BottomAppBar, AA.Add, AA.Book, AA.Button])
    w__assert_element_not_existing(c, [AA.BottomAppBar, AA.NextPage, AA.Button])


@then('[next page button] is showing in bottom app bar')
def then__next_page_button_is_showing_in_bottom_app_bar(c):
    elm = w__get_element_by_shown_dom_id(c, [AA.BottomAppBar, AA.NextPage, AA.Button])
    assert elm is not None


@when('{mentor} click on [next page button] on bottom app bar')
def when__click_on_next_page_button__on_bottom_app_bar(c, mentor: str):
    w__click_element_by_dom_id(c, [AA.BottomAppBar, AA.NextPage, AA.Button])


@when('{mentor} click on [Page {page_str} Button] on page list bar')
def when__click_on_page_button_on_page_controller(c, mentor: str, page_str: str):
    page_str = BehaveUtil.clear_string(page_str)
    w__click_element_by_dom_id(c, [AA.Page, page_str, AA.Button])


@when('{mentor} click on [Last Page Button] on page list bar')
def when__click_on_last_page_button_on_page_list_bar(c, mentor: str):
    page_bar = w__get_element_by_shown_dom_id(c, [AA.Page, AA.Bar])
    btn_list = page_bar.find_elements(by=By.XPATH, value=f"./button")
    click_element(c, btn_list[-1])