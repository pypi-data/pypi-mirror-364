from volworld_common.api.CA import CA
from volworld_common.test.behave.BehaveUtil import BehaveUtil

from volworld_aws_api_common.test.behave.row_utils import w__get_row_items
from volworld_aws_api_common.test.behave.selenium_utils import w__click_element_by_dom_id, \
    w__get_element_by_shown_dom_id, w__get_element_by_presence_dom_id, w__assert_element_not_existing, \
    get_element_by_dom_id


def click_on_page_in_page_container(c, page_str: str):
    page_str = BehaveUtil.clear_string(page_str)
    w__click_element_by_dom_id(c, [CA.Page, page_str, CA.Button])


def assert_pagination_of_list_page_count(c, count: int, total_page_count: int, total_item_count_str: str = ''):
    rows = w__get_row_items(c)
    assert len(rows) == count, f"found [{len(rows)}] books != [{count}] = expect"

    pg1_id = [CA.Page, '1', CA.Button]
    # assert page button
    if total_page_count > 1:
        last_pg_id = [CA.Page, f"{total_page_count}", CA.Button]
        no_pg_id = [CA.Page, f"{total_page_count + 1}", CA.Button]
        print(f'last_pg_id = [{last_pg_id}]')
        print(f'no_pg_id = [{no_pg_id}]')
        w__get_element_by_presence_dom_id(c, last_pg_id)
        w__assert_element_not_existing(c, no_pg_id)

    # assert book count
    elm = get_element_by_dom_id(c, [CA.Page, CA.TotalCount])
    all_book_count = int(elm.get_attribute('innerHTML').strip())
    if len(total_item_count_str) > 0:
        total_book_count = BehaveUtil.clear_int(total_item_count_str)
        assert all_book_count == total_book_count

    # not showing page button
    if total_page_count <= 1:
        w__assert_element_not_existing(c, pg1_id)
        return

    # if total_page_count <= 1:
    #     w__assert_element_not_existing(c, [A.Page, A.Info])
    #     return
    # elm = w__get_element_by_shown_dom_id(c, [A.Page, A.Info])
    # info = get_elm_text(elm)
    # all_page_count = int(info.split('/')[1].strip())
    # assert total_page_count == all_page_count


def assert_current_page(c, page_str: str):
    elm = w__get_element_by_shown_dom_id(c, [CA.Page, BehaveUtil.clear_string(page_str), CA.Button])
    assert elm.get_attribute("data-btn-info") == "curr"

    # class_list = elm.get_attribute("class").split()
    # found_curr_class = False
    # for c in class_list:
    #     if c.find('StPagination_CurrButton') > -1:
    #         found_curr_class = True
    #         break
    # assert found_curr_class



