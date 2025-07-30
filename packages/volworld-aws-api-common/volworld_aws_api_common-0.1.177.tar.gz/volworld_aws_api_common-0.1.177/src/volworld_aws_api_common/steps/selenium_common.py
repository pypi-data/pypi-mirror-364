from behave import *


@when('"{mentor}" click on [back] button on browser')
def click_on_button(c, mentor: str):
    c.browser.back()