from tests.test_base_selenium import SeleniumTestBase
from selenium.webdriver.common.keys import Keys
import time
import pdb


class TestGoogle(SeleniumTestBase):

    def test_make_sure_google_search_works(self):
        """
        Given a browser
        When a search for "testing" in google is made
        Then some pages are returned
        """
        self.log_step("When a search for 'testing' in google is made")
        self.client.get('http://www.google.com')
        search = self.client.find_element_by_name('q')
        search.send_keys("testing")
        search.send_keys(Keys.RETURN)  # hit return after you enter search text
        time.sleep(5)  # sleep for 5 seconds so you can see the results

        self.log_step("Then some pages are returned")
        results_count = len(self.client.find_elements_by_css_selector(".g"))
        self.add_output_message("Results Count: {}".format(results_count))
        if results_count <= 0:
            self.add_fail_message("No results found")

        self.then_everything_should_be_fine()
