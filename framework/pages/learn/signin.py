from framework.pages.page_base import *
import pdb

# Separating Locators may seen interesting to load these selectors from somewhere else (a model?) in the future
# Idea/Code inspired on https://github.com/gunesmes/page-object-python-selenium/blob/master/locators.py


class LocatorsSigInMain(LocatorsBase):
    DESKTOP_HEADER = (By.TAG_NAME, 'desktop-page-header')
    GOTIT_BUTTON = (By.CLASS_NAME, 'cc_btn_accept_all')
    LOGIN_BUTTON = (By.CSS_SELECTOR, '.e2e-login-link')


class LocatorsSigInForm(LocatorsBase):
    LOGIN_BUTTON = (By.ID, 'log-in-button')
    LOGIN_EMAIL = (By.ID, 'email-address-input')
    LOGIN_PASSWORD = (By.ID, 'password-input')


class LocatorsLearn(LocatorsBase):
    AVATAR = (By.CSS_SELECTOR, '.e2e-avatar')


class PageSigInMain(PageBase):
    def __init__(self, browser: Browser, url: str):
        super().__init__(browser, LocatorsSigInMain(), url, 3)

    def login(self, user, passwd):
        try:
            self.open()

            self.LOGIN_BUTTON.click()
            self.add_to_output("LOGIN_BUTTON clicked")

            self.load(LocatorsSigInForm())
            self.LOGIN_EMAIL.type(user.replace("\"", ""))
            self.LOGIN_PASSWORD.type(passwd.replace("\"", ""), hide=True)
            self.browser.set_timeout(60)
            self.add_to_output("Credentials used")

            self.LOGIN_BUTTON.click()
            self.load(LocatorsLearn())
            self.AVATAR.wait_for_visible(3)
            self.add_to_output("AVATAR loaded")
        except Exception as e:
            self.exception_to_error_message(e)
        return self


class PageLearn(PageBase):
    def __init__(self, browser: Browser):
        super().__init__(browser, LocatorsLearn(), timeout=3)

    def is_logged_in(self):
        try:
            self.AVATAR.wait_for_visible(3)
            self.add_to_output("AVATAR loaded")
        except Exception as e:
            self.exception_to_error_message(e)
        return self