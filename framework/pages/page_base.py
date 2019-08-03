from framework.log.logger import Logger
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from framework.datetime.datetime import now_to_str
from typing import List
import os


class Browser:
    def __init__(self, browser):
        self.browser = browser
        base_directory = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-2])
        self.screenshots_directory = os.path.join(base_directory, "logs")
        self.logger = Logger(name=self.__class__.__name__)
        self.timeout = 0

    def open(self, url):
        if url is not None and url != self.browser.current_url:
            self.browser.get(url)
            self.logger.log("Opened {}".format(url))

    def close(self):
        self.browser.close()

    def set_timeout(self, timeout: int):
        if not timeout or timeout <= 0:
            return
        self.browser.implicitly_wait(timeout)
        self.logger.log("Set implicit wait to {}".format(timeout))
        self.timeout = timeout

    def find_element(self, by, value):
        return self.browser.find_element(by, value)

    def save_screenshot(self, prefix=None):
        filename = "{}.{}.png".format(prefix, now_to_str())
        full_filename = os.path.join(self.screenshots_directory, filename)
        self.browser.save_screenshot(filename=full_filename)
        self.logger.log("Screenshot saved on {}".format(full_filename))
        return full_filename

    def save_html(self, prefix=None):
        filename = "{}.{}.html".format(prefix, now_to_str())
        full_filename = os.path.join(self.screenshots_directory, filename)
        with open(full_filename, "w", encoding="utf-8") as f:
            f.write(self.browser.page_source)
        self.logger.log("HTML saved on {}".format(full_filename))
        return full_filename


class LocatorsBase:
    def items(self):
        return {
            a: getattr(self, a)
            for a in dir(self)
            if not callable(getattr(self, a)) and not a.startswith("_")
        }.items()


class Element:
    def __init__(self, browser: Browser, name, locator, timeout):
        self.browser = browser
        self.name = name
        self.locator = locator
        self.timeout = timeout
        self.logger = Logger(name=name)
        self.element = browser.find_element(*locator)
        self.logger.log("Found")

    def click(self, timeout=None):
        wait_time = timeout if timeout else self.timeout
        self.wait_for_visible(wait_time)
        try:
            self.logger.log("Click")
            self.element.click()
        except Exception as e:
            self.handle_exception(e)

    def type(self, message, hide=False):
        self.logger.log("Typying {} with hide = {}".format(message if not hide else "*"*len(message), hide))
        self.element.send_keys(message)

    def wait_for_visible(self, timeout=None):
        wait_time = timeout if timeout else self.browser.timeout
        self.logger.log("Waiting for visibility during {}s".format(wait_time))
        try:
            WebDriverWait(self.browser, wait_time).until(expected_conditions.visibility_of_element_located(self.locator))
        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, e):
        exeption_type = e.__class__.__name__
        self.logger.log("{} raised".format(exeption_type))
        self.browser.save_screenshot("{}.{}".format(self.name, exeption_type))
        self.browser.save_html("{}.{}".format(self.name, exeption_type))
        raise Exception("{} on {}".format(exeption_type, self.name))


class PageBase:
    """
    @DynamicAttrs loaded as part of load()
    """
    def __init__(self, browser: Browser, locators: LocatorsBase, url: str = None, timeout: int = None):
        self.browser = browser
        self.locators = locators
        self.url = url
        self.timeout = timeout
        self.elements: List[Element] = []
        browser.set_timeout(timeout)

        # error messages that will make tests fails
        self.error_messages = []

        # log messages to be used for logging in pytest results
        self.output_messages = []

        # Other useful declarations for the children to use
        self.logger = Logger(name=self.__class__.__name__)

    def exception_to_error_message(self, e):
        html_file = self.browser.save_html(self.__class__.__name__)
        screenshot_file = self.browser.save_screenshot(self.__class__.__name__)
        message = "[{}] {} - Saved HTML in {} and screenshot in {}".format(
            self.__class__.__name__,
            e,
            html_file,
            screenshot_file
        )
        self.error_messages.append(message)
        self.output_messages.append(message)

    def open(self):
        self.browser.open(self.url)
        self.load()
        return self

    def load(self, locators: LocatorsBase = None):
        expected_locators = locators if locators else self.locators
        for name, locator in expected_locators.items():
            self.logger.log("Loading {}".format(name))
            element = None
            try:
                element = Element(self.browser, name, locator, self.timeout)
                self.elements.append(element)
            except Exception as e:
                self.logger.log("{} = NONE, {}".format(name, e))
            self.__dict__[name] = element

