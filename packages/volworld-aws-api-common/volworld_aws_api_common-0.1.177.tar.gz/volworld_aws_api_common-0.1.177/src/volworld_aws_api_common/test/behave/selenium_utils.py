import time

import selenium
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from volworld_aws_api_common.api.dom_id import dom_id
from volworld_aws_api_common.api.AA import AA


def waiting_for_animation():
    time.sleep(0.5)


def get_elm_text(elm) -> str:
    return elm.get_attribute('innerHTML').strip()


def click_element(context, elm):
    ActionChains(context.browser).click(elm).perform()


def click_element_by_dom_id(c, ids: list) -> WebElement:
    elm = get_element_by_dom_id(c, ids)
    assert elm is not None
    click_element(c, elm)
    return elm


def w__get_element_by_shown_dom_id(c, ids: list) -> WebElement:
    tar_id = dom_id(ids)
    print(f"[GET] get_element_by_dom_id [{tar_id}]")
    return c.wait.until(EC.visibility_of_element_located((By.ID, tar_id)))


def w__get_element_by_clickable_dom_id(c, ids: list) -> WebElement:
    tar_id = dom_id(ids)
    print(f"[GET] get_element_by_dom_id [{tar_id}]")
    return c.wait.until(EC.element_to_be_clickable((By.ID, tar_id)))


def w__get_element_by_presence_dom_id(c, ids: list) -> WebElement:
    tar_id = dom_id(ids)
    print(f"[GET] get_element_by_dom_id [{tar_id}]")
    return c.wait.until(EC.presence_of_element_located((By.ID, tar_id)))


def w__get_element_by_shown_xpath(c, xpath: str) -> WebElement:
    print(f"[GET] get_element_by_xpath [{xpath}]")
    return c.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))


def w__click_element_by_dom_id(c, ids: list) -> WebElement:
    elm = w__get_element_by_clickable_dom_id(c, ids)
    click_element(c, elm)
    return elm


def w__assert_element_existing(c, ids: list) -> WebElement:
    elm = w__get_element_by_shown_dom_id(c, ids)
    assert elm is not None, f"Element of {ids} is NOT found."
    return elm


def get_element_by_dom_id(c, ids: list) -> WebElement:
    tar_id = dom_id(ids)
    elms = c.browser.find_elements(By.XPATH, f"//*[@id='{tar_id}']")
    if len(elms) == 0:
        return None
    assert len(elms) == 1
    return elms[0]


def wait_element_to_disappear(c, tar_id, sec: float) -> bool:
    time.sleep(sec)
    elms = c.browser.find_elements(By.XPATH, f"//*[@id='{tar_id}']")
    return len(elms) == 0


def w__assert_element_not_existing(c, ids: list):
    tar_id = dom_id(ids)
    if wait_element_to_disappear(c, tar_id, 0.1):
        return
    print(f'Waining [{tar_id}] to disappear for [{0.2}] sec')
    if wait_element_to_disappear(c, tar_id, 0.2):
        return
    print(f'Waining [{tar_id}] to disappear for [{0.3}] sec')
    if wait_element_to_disappear(c, tar_id, 0.3):
        return
    print(f'Waining [{tar_id}] to disappear for [{0.5}] sec')
    if wait_element_to_disappear(c, tar_id, 0.5):
        return
    print(f'Waining [{tar_id}] to disappear for [{0.8}] sec')
    assert wait_element_to_disappear(c, tar_id, 0.8), f"Element of {tar_id} is existing."


def check_have_class(el, class_name) -> bool:
    return class_name in el.get_attribute('class').split()


def check_have_svg_icon(svg, class_list: list) -> bool:
    return check_have_class(svg, f"SvgIcon-{'-'.join(class_list)}")


def check_page_id(driver, exp_page_id: str):
    page_id = driver.find_element(By.ID, dom_id([AA.Page, AA.Id]))
    if not page_id:
        return False
    # page_id = w__get_element_by_presence_dom_id(c, [A.Page, A.Id])
    if page_id.get_attribute('innerHTML').strip() == exp_page_id:
        return True # page_id
    return False


def assert_page_id(c, exp_page_id: str):
    c.wait.until(lambda wd: check_page_id(wd, exp_page_id))

    # page_id = w__get_element_by_presence_dom_id(c, [AA.Page, AA.Id])
    # assert page_id.get_attribute('innerHTML').strip() == exp_page_id, \
    #     f"Curr Page Id = [{page_id.get_attribute('innerHTML').strip()}] != [{exp_page_id}]"


def predicate__get_page_id(c, exp_page_id: str):
    def _predicate(driver):
        try:
            page_id = get_element_by_dom_id(c, [AA.Page, AA.Id])
            if page_id is None:
                return None
            if page_id.get_attribute('innerHTML').strip() == exp_page_id:
                return page_id
            return None
        except Exception as err:
            print("Exception for get page_id! ", err)
            return None

    return _predicate


def w__assert_page_id(c, exp_page_id: str):
    elm = c.wait.until(predicate__get_page_id(c, exp_page_id))
    waiting_elm = get_element_by_dom_id(c, [AA.Waiting, AA.Load])
    if waiting_elm is not None:
        tar_id = dom_id([AA.Finished, AA.Load])
        return WebDriverWait(c.browser, 20).until(EC.presence_of_element_located((By.ID, tar_id)))

    return elm


def scroll_down(c, pix: int):
    c.browser.execute_script(f'scrollBy(0, {pix})')


def scroll_to_bottom(c):
    c.browser.execute_script(f'window.scrollTo(0, document.body.scrollHeight)')


def w__key_in_element_by_dom_id(c, ids: list, input_str: str, clear=True) -> WebElement:
    elm = w__get_element_by_shown_dom_id(c, ids)
    if clear:
        elm.send_keys(Keys.CONTROL + "a")
        elm.send_keys(Keys.DELETE)
    elm.send_keys(input_str)
    return elm


def click_list_nav__sort_by(c, prefix=None) -> WebElement:
    if prefix is None:
        prefix = list()
    return w__click_element_by_dom_id(c, prefix + [AA.List, AA.Navigator, AA.Button, AA.SortBy])


def click_list_nav__sort_direction(c, prefix=None) -> WebElement:
    if prefix is None:
        prefix = list()
    return w__click_element_by_dom_id(c, prefix + [AA.List, AA.Navigator, AA.Button, AA.SortDirection])


def click_list_nav__tag_info(c, prefix=None) -> WebElement:
    if prefix is None:
        prefix = list()
    return w__click_element_by_dom_id(c, prefix + [AA.List, AA.Navigator, AA.Button, AA.Tag])



'''
@note copy & paste can NOT work in headless Jenkins tests
'''
def input_large_content_to_text_input(c, elm, content):
    # print(f"content = {content}")
    # print(f"elm = {elm}")
    elm.click()
    time.sleep(0.3)
    c.browser.execute_script("arguments[0].value = arguments[1]", elm, content)
    time.sleep(0.3)
    elm.send_keys(Keys.ARROW_RIGHT)  # cancel selection
    elm.send_keys(Keys.SPACE)
    try:
        elm.send_keys(Keys.BACKSPACE)  # for activate JS
    except:
        print("Can NOT keyin BACKSPACE")
