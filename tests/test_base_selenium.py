from tests.test_base import ApiTestBase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pytest


# Greatly inspired by https://github.com/CircleCI-Public/circleci-demo-python-flask/blob/master/tests/test_selenium.py
class SeleniumTestBase(ApiTestBase):
    client = None

    @classmethod
    def setUpClass(cls):
        try:
            chrome_options = Options()
            chrome_options.add_argument("start-maximized")  # openBrowser in maximized mode
            chrome_options.add_argument("disable-infobars")  # disabling infobars
            chrome_options.add_argument('--headless')  # headless for faster execution
            chrome_options.add_argument("--disable-extensions")  # disabling extensions
            chrome_options.add_argument("--disable-gpu")  # applicable to windows only
            chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
            chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
            cls.client = webdriver.Chrome(
                ChromeDriverManager(version="75.0.3770.140").install(),
                chrome_options=chrome_options,
                service_args=["--verbose", "--log-path=logs/chrome.log"]
            )
            cls.client_err = ''
        except Exception as e:
            cls.client_err = str(e)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.close()

    def setUp(self):
        super().setUp()
        if not self.client:
            self.log('Web browser not available')
            self.log(self.client_err)
            pytest.skip()

    def tearDown(self):
        super().tearDown()