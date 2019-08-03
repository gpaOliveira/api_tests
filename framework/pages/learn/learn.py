from framework.pages.page_base import *
import pdb

# Separating Locators may seen interesting to load these selectors from somewhere else (a model?) in the future
# Idea/Code inspired on https://github.com/gunesmes/page-object-python-selenium/blob/master/locators.py


class LocatorsLearnNotLoggedIn(LocatorsBase):
    DESKTOP_HEADER = (By.TAG_NAME, 'desktop-page-header')
    GOTIT_BUTTON = (By.CLASS_NAME, 'cc_btn_accept_all')
    LOGIN_BUTTON = (By.CSS_SELECTOR, '.e2e-login-link')


class LocatorsAccountLogin(LocatorsBase):
    LOGIN_BUTTON = (By.ID, 'log-in-button')
    LOGIN_EMAIL = (By.ID, 'email-address-input')
    LOGIN_PASSWORD = (By.ID, 'password-input')


class LocatorsLearn(LocatorsBase):
    AVATAR = (By.CSS_SELECTOR, '.e2e-avatar')


class PageLearn(PageBase):
    def __init__(self, browser: Browser, url: str):
        super().__init__(browser, LocatorsLearnNotLoggedIn(), url, 3)

    def login(self, user, passwd):
        try:
            self.open()
            
            self.LOGIN_BUTTON.click()
            self.output_messages.append("LOGIN_BUTTON clicked")

            self.load(LocatorsAccountLogin())
            self.LOGIN_EMAIL.type(user.replace("\"", ""))
            self.LOGIN_PASSWORD.type(passwd.replace("\"", ""), hide=True)
            self.browser.set_timeout(60)
            self.output_messages.append("Credentials used")

            self.LOGIN_BUTTON.click()
            self.load(LocatorsLearn())
            self.AVATAR.wait_for_visible(3)
            self.output_messages.append("AVATAR loaded")
        except Exception as e:
            self.exception_to_error_message(e)

        return self
