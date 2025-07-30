from behave import *
from volworld_aws_api_common.test.behave.row_utils import (
    update_order_type_of_list, w__tags_of_all_rows_are_showing, w__tags_of_all_rows_are_not_showing)

from volworld_aws_api_common.api.AA import AA
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id


@when('{mentor} update [order] type of list page to {sort_dir}')
def when__update_order_type_of_list_page(c, mentor: str, sort_dir: str):
    update_order_type_of_list(c, sort_dir)


@then('tags of all rows are showing')
def then__tags_of_all_rows_are_showing(c):
    w__tags_of_all_rows_are_showing(c)


@then('tags of all rows are not showing')
def then__tags_of_all_rows_are_not_showing(c):
    w__tags_of_all_rows_are_not_showing(c)


@then('there is no row in list page')
def then__there_is_no_row_in_list_page(c):
    elm = w__get_element_by_shown_dom_id(c, [AA.Empty, AA.InfoRow, AA.List])
    assert elm is not None