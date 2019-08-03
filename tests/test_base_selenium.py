from tests.test_base import ApiTestBase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from framework.pages.page_base import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pytest


# Greatly inspired by https://github.com/CircleCI-Public/circleci-demo-python-flask/blob/master/tests/test_selenium.py
class SeleniumTestBase(ApiTestBase):
    browser = None
    client_err = ''

    def create_browser(self):
        # Really not sure if we need a singleton, as I'm seeing "invalid session id errors",
        # so leaving it here for now
        # if SeleniumTestBase.browser:
        #     self.browser = SeleniumTestBase.browser
        #     return SeleniumTestBase.browser
        try:
            chrome_options = Options()
            chrome_options.add_argument("disable-infobars")  # disabling infobars
            chrome_options.add_argument('--headless')  # headless for faster execution
            chrome_options.add_argument("--disable-extensions")  # disabling extensions
            chrome_options.add_argument("--disable-gpu")  # applicable to windows only
            chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
            chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
            browser = webdriver.Chrome(
                ChromeDriverManager(version="75.0.3770.140").install(),
                chrome_options=chrome_options,
                service_args=["--verbose", "--log-path=logs/chrome.log"]
            )
            browser.set_window_size(1920, 1080, browser.window_handles[0])
            SeleniumTestBase.browser = Browser(browser)
            SeleniumTestBase.browser.set_timeout(1)
            SeleniumTestBase.client_err = ''
            self.browser = SeleniumTestBase.browser
        except Exception as e:
            SeleniumTestBase.client_err = str(e)

    @classmethod
    def tearDownClass(cls):
        if cls.browser:
            cls.browser.close()

    def setUp(self):
        super().setUp()
        self.create_browser()
        if not self.browser:
            self.log('Web browser not available')
            self.log(self.client_err)
            pytest.skip()

    def tearDown(self):
        super().tearDown()