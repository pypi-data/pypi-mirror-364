from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from volworld_common.api.CA import CA

from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.behave.selenium_utils import get_element_by_dom_id, w__click_element_by_dom_id, \
    w__get_element_by_shown_dom_id
from volworld_aws_api_common.test.behave.drawer_utils import click_to_open_list_nav_drawer


def assert_tag_svg_class_of_all_rows(rows, class_name_list: list):
    class_name = f"SvgIcon-{'-'.join(class_name_list)}"
    for r in rows:
        main = r.find_element(By.XPATH, "./main/nav/main")  # @note xpath can NOT find svg element
        main_inner = main.get_attribute('innerHTML')
        assert main_inner.find(class_name) > -1, \
            f"Class [{class_name}] NOT in tag main svg classes = [{main_inner}]"


def predicate__get_row_container(c):
    def _predicate(driver):
        container_ids = ([CA.InfoRow, CA.List], [CA.Book, CA.List], [CA.Chapter, CA.List], [CA.Word, CA.List])
        list_container = None
        for con_id in container_ids:
            list_container = get_element_by_dom_id(c, con_id)
            if list_container is not None:
                break
        return list_container

    return _predicate


def w__get_row_container(c):
    return c.wait.until(predicate__get_row_container(c))


def predicate__tags_of_all_rows_are_showing(c):
    def _predicate(driver):
        rows = w__get_row_items(c)
        assert len(rows) > 0, 'Can NOT find rows'
        tag_nav_list = get_tag_element_list(c)
        if len(tag_nav_list) == 0:
            return None
        if len(rows) == len(tag_nav_list):
            return tag_nav_list[0]
        return None

    return _predicate


def w__tags_of_all_rows_are_showing(c):
    return c.wait.until(predicate__tags_of_all_rows_are_showing(c))


def predicate__tags_of_all_rows_are_not_showing(c):
    def _predicate(driver):
        rows = w__get_row_items(c)
        assert len(rows) > 0, 'Can NOT find rows'
        tag_nav_list = get_tag_element_list(c)
        if len(tag_nav_list) == 0:
            return rows[0]
        if len(rows) == len(tag_nav_list):
            return None
        return None

    return _predicate


def w__tags_of_all_rows_are_not_showing(c):
    return c.wait.until(predicate__tags_of_all_rows_are_not_showing(c))


def w__get_row_items(c) -> list:
    list_container = w__get_row_container(c)

    assert list_container is not None, 'Can NOT find row item container'
    return list_container.find_elements(By.XPATH, "./div")


def get_row__tag_info__as__text_list(c) -> list:
    rows = w__get_row_items(c)
    tag_text_list = []
    for r in rows:
        span = r.find_element(By.XPATH, "./main/nav/main/b")
        tag_text_list.append(span.get_attribute('innerHTML').strip())
    return tag_text_list


def get_row__tag_info__as__int_list(c) -> list:
    info = get_row__tag_info__as__text_list(c)
    int_info = []
    for i in info:
        int_info.append(int(i))
    return int_info


def get_row__text__as__text_list(c) -> list:
    rows = w__get_row_items(c)
    row_text_list = []
    for r in rows:
        span = r.find_element(By.XPATH, "./main/main/span")
        row_text_list.append(span.get_attribute('innerHTML').strip())
    return row_text_list


def get_tag_element_list(c) -> list:
    rows = w__get_row_items(c)
    row_tag_nav_list = []
    for r in rows:
        try:
            tag_nav = r.find_element(By.XPATH, "./main/nav")
            row_tag_nav_list.append(tag_nav)
        except NoSuchElementException:
            pass
    return row_tag_nav_list


def update_order_type_of_list(c, sort_dir: str):
    sort_dir = BehaveUtil.clear_string(sort_dir)
    click_to_open_list_nav_drawer(c, CA.SortDirection)
    if sort_dir.lower() == "ascending":
        w__click_element_by_dom_id(c, [CA.SortDirection, CA.Drawer, CA.Ascending, CA.Button])
    if sort_dir.lower() == "descending":
        w__click_element_by_dom_id(c, [CA.SortDirection, CA.Drawer, CA.Descending, CA.Button])


def check_tag_svg_class_of_all_rows(rows, class_name_list: list):
    def _predicate(driver):
        class_name = f"SvgIcon-{'-'.join(class_name_list)}"
        for r in rows:
            main = r.find_element(By.XPATH, "./main/nav/main")  # @note xpath can NOT find svg element
            main_inner = main.get_attribute('innerHTML')
            if main_inner.find(class_name) < 0:
                print("can not find class_name = ", class_name)
                return False
        return True

    return _predicate


def w__assert_tag_svg_class_of_all_rows(c, rows, class_name_list: list):
    return c.wait.until(check_tag_svg_class_of_all_rows(rows, class_name_list))


def load_row_text_list(c) -> list:
    elm = w__get_row_container(c)
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./div/main/main/span")
    row_text_list = []
    for r in rows:
        row_text_list.append(r.get_attribute('innerHTML').strip())
        # print(r.get_attribute('innerHTML').strip())
    return row_text_list


def load_row_tag_info_list(c) -> list:
    elm = w__get_row_container(c)
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./div/main/nav/main/b")
    row_tag_info_list = []
    for r in rows:
        row_tag_info_list.append(r.get_attribute('innerHTML').strip())
        print(r.get_attribute('innerHTML').strip())
    return row_tag_info_list


def assert_tag_icon_class_of_list(c, _class):
    elm = w__get_row_container(c)
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./div/main/nav/main")
    # row_class_list = []
    for r in rows:
        # row_class_list.append(r.get_attribute('innerHTML').strip())
        inner = r.get_attribute('innerHTML').strip()
        assert inner.find(_class) > -1, f"Can NOT find [{_class}] in \n{inner}"
        # print(r.get_attribute('innerHTML').strip())
    # return row_class_list


def get_info_row_element_by_svg_name(c, row_index: int, elm_tag: str, svg_class_name: str):
    row_container = w__get_element_by_shown_dom_id(c, [CA.InfoRow, CA.List])
    assert row_container is not None
    rows = row_container.find_elements(By.XPATH, "./div/main/aside")
    collect_btn_lst = rows[row_index].find_elements(By.XPATH, f"./{elm_tag}")
    print(f"found [{len(collect_btn_lst)}] {row_container}")
    for btn in collect_btn_lst:
        svg_lst = btn.find_elements(By.XPATH, f"./*[name()='svg' and contains(@class, '{svg_class_name}')]")
        if len(svg_lst) > 0:
            assert len(svg_lst) == 1
            return btn
    return None


def get_info_row_button_by_svg_name(c, row_index: int, svg_class_name: str):
    return get_info_row_element_by_svg_name(c, row_index, 'button', svg_class_name)


def get_info_row_link_by_svg_name(c, row_index: int, svg_class_name: str):
    return get_info_row_element_by_svg_name(c, row_index, 'a', svg_class_name)