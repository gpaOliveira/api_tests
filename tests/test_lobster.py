from tests.test_base_selenium import SeleniumTestBase
from framework.pages.learn.signin import PageSigInMain
from framework.pages.learn.signup import *
import pdb


class TestLobster(SeleniumTestBase):

    def test_lobster_login(self):
        """
        Given LOBSTER_EMAIL and LOBSTER_PASSWORD are provided
        When we navigate and login
        Then everything is fine
        """
        self.log_step("Given a LOBSTER_EMAIL")
        if not self.environment.LOBSTER_EMAIL:
            self.then_everything_should_be_fine(["No LOBSTER_EMAIL"])
        self.log_step("Given a LOBSTER_PASSWORD")
        if not self.environment.LOBSTER_PASSWORD:
            self.then_everything_should_be_fine(["No LOBSTER_PASSWORD"])

        self.log_step('When we navigate and login')
        learn = (
            PageSigInMain(self.browser, url=self.environment.LOBSTER_MY_LEARN).
            login(self.environment.LOBSTER_EMAIL, self.environment.LOBSTER_PASSWORD)
        )
        self.flush_page_messages(learn)

        self.then_everything_should_be_fine()

    def test_lobster_signup_random_user(self):
        """
        Given LOBSTER_PASSWORD is provided
        When we signup a new random user
        Then everything is fine
        """
        self.log_step("Given a LOBSTER_PASSWORD")
        if not self.environment.LOBSTER_PASSWORD:
            self.then_everything_should_be_fine(["No LOBSTER_PASSWORD"])

        self.log_step('When we signup a new random user')
        learn = (
            PageSignUpMain(self.browser, url=self.environment.LOBSTER_MY_LEARN).
            signup_start().
            by_email().
            with_random_user(self.environment.LOBSTER_PASSWORD).
            is_logged_in()
        )
        self.flush_page_messages(learn)

        self.then_everything_should_be_fine()
