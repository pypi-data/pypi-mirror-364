from behave import *


@when('clear browser local storage')
def when__clear_local_storage(c):
    c.browser.execute_script("window.localStorage.clear();")


@when('refresh browser')
def when__refresh_browser(c):
    c.browser.refresh()
