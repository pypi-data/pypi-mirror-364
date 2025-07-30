from behave import *
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, w__click_element_by_dom_id
from volworld_aws_api_common.api.AA import AA


@then('[save button] is disabled')
def then__the_save_button_is_disabled(c):
    elm = w__get_element_by_shown_dom_id(c, [AA.Save, AA.Button])
    assert not elm.is_enabled()


@then('[save button] is enabled')
def then__the_save_button_is_enabled(c):
    elm = w__get_element_by_shown_dom_id(c, [AA.Save, AA.Button])
    assert elm.is_enabled()


@when('{user} click on [save button]')
def when__click_on_save_button(c, user: str):
    w__click_element_by_dom_id(c, [AA.Save, AA.Button])


@then('[ok button] is disabled')
def then__the_ok_button_is_disabled(context):
    elm = w__get_element_by_shown_dom_id(context, [AA.Ok, AA.Button])
    assert not elm.is_enabled()


@then('[ok button] is enabled')
def then__the_ok_button_is_enabled(context):
    elm = w__get_element_by_shown_dom_id(context, [AA.Ok, AA.Button])
    assert elm.is_enabled()


@when('{user} click on [ok button]')
def when__click_on_ok_button(context, user: str):
    w__click_element_by_dom_id(context, [AA.Ok, AA.Button])


@when('{user} click on [cancel button]')
def when__click_on_cancel_button(context, user: str):
    w__click_element_by_dom_id(context, [AA.Cancel, AA.Button])


@when('{user} click on dialog [cancel button]')
def when__click_on_dialog_cancel_button(context, user: str):
    w__click_element_by_dom_id(context, [AA.Dialog, AA.Cancel, AA.Button])


@when('{user} click on dialog [ok button]')
def when__click_on_dialog_ok_button(context, user: str):
    w__click_element_by_dom_id(context, [AA.Dialog, AA.Ok, AA.Button])


@when('{user} click on dialog [save button]')
def when__click_on_dialog_save_button(context, user: str):
    w__click_element_by_dom_id(context, [AA.Dialog, AA.Save, AA.Button])