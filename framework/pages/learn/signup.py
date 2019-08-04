from framework.pages.page_base import *
from framework.datetime.datetime import now_to_str
from framework.pages.learn.signin import PageLearn


class LocatorsSignUpMain(LocatorsBase):
    DESKTOP_HEADER = (By.TAG_NAME, 'desktop-page-header')
    SIGNUP_BUTTON = (By.CLASS_NAME, 'e2e-signup-link')


class LocatorsSignUpMethods(LocatorsBase):
    SIGNUP_EMAIL = (By.ID, 'sign-up-with-email')


class LocatorsSignUpForm(LocatorsBase):
    FIRSTNAME_INPUT = (By.ID, 'FirstName')
    LASTNAME_INPUT = (By.ID, 'LastName')
    EMAIL_INPUT = (By.ID, 'Email')
    CONFIRM_EMAIL_INPUT = (By.ID, 'ConfirmEmail')
    PASSWORD_INPUT = (By.ID, 'Password')
    CONFIRM_PASSWORD_INPUT = (By.ID, 'ConfirmPassword')
    SIGNUP_BUTTON = (By.ID, 'sign-up-button')


class PageSignUpForm(PageBase):
    def __init__(self, browser: Browser):
        super().__init__(browser, LocatorsSignUpForm(), timeout=3)
        self.user = ''
        self.email = ''
        self.password = ''

    def with_random_user(self, password):
        self.user = "test-user-" + now_to_str()
        self.email = self.user + "@email.com"
        try:
            self.FIRSTNAME_INPUT.type("Test")
            self.LASTNAME_INPUT.type("User")
            self.EMAIL_INPUT.type(self.email.replace("\"", ""))
            self.CONFIRM_EMAIL_INPUT.type(self.email.replace("\"", ""))
            self.PASSWORD_INPUT.type(password.replace("\"", ""), hide=True)
            self.CONFIRM_PASSWORD_INPUT.type(password.replace("\"", ""), hide=True)
            self.SIGNUP_BUTTON.click(10)
            self.add_to_output("SIGNUP_BUTTON clicked with user '{}'".format(self.email))
        except Exception as e:
            self.exception_to_error_message(e)
        return self.load_new_page(PageLearn)


class PageSignUpMethod(PageBase):
    def __init__(self, browser: Browser):
        super().__init__(browser, LocatorsSignUpMethods(), timeout=3)

    def by_email(self):
        try:
            self.SIGNUP_EMAIL.click(timeout=10)
            self.add_to_output("SIGNUP_EMAIL clicked")
        except Exception as e:
            self.exception_to_error_message(e)
        return self.load_new_page(PageSignUpForm)


class PageSignUpMain(PageBase):
    def __init__(self, browser: Browser, url: str):
        super().__init__(browser, LocatorsSignUpMain(), url, 3)

    def signup_start(self):
        try:
            self.open()
            self.SIGNUP_BUTTON.click(timeout=10)
            self.add_to_output("SIGNUP_BUTTON clicked")
        except Exception as e:
            self.exception_to_error_message(e)
        return self.load_new_page(PageSignUpMethod)


