[![CircleCI](https://circleci.com/gh/gpaOliveira/api_tests.svg?style=svg)](https://circleci.com/gh/gpaOliveira/api_tests)

Minimalistic Python 3.6.1 framework to create/run API tests with Pytest, generating a nice HTML and JUnit XML in the end.

Currently supporting:
* Gitlab API (https://docs.gitlab.com/ee/api/README.html)
* Pokemon API (https://pokeapi.co/)
* Lobster UI/API (https://my.lobsterink.com/learn)

Install with
```bash
setup install
```

Before executing, remember to export/set (if in linux or windows) some variables required by some tests (or to define them on environment.json at framework/environment/environment.json):
```bash
export GITLAB_KEY="<your-private-key>"
export GITHUB_KEY="<your-private-key>"
export LOBSTER_EMAIL="<your-private-key>"
export LOBSTER_PASSWORD="<your-private-key>"
```

Then run tests with:
```bash
pytest tests/
```

### Test details:

The framework is based on API objects (inherited from framework/apis/api_base.py) generating and using Data objects to allow tests the necessary flexibility to deal with data coming from multiple sources. There's also support for UI Page Objects (inherited from framework/pages/page_base.py) but there are not yet yielding Data objects as they could.

Additionally, a test framework requires certain other features, such as environment variables and logging. These are accessible throgh the ApiTestBase (tests/test_base.py) class, that should be inherited by all test classes.

Environment variables are controlled by the Environment package and class (framework/environment/environment.py), a custom made class that either load variables from a JSON file (framework/environment/environment.json) or from the OS (added using 'export' on Linux, for example). Thus, all tests have access to environment variables on runtime, through ApiTestBase.environment. For example, the value for GITLAB_KEY is accessible with ```self.environment.GITLAB_KEY```.

Logging is controlled by the Logger class (framework/log/logger.py), another custom made class that allow all classes access to a test log file, that is showed in the ```stdout``` and in a proper file under logs folder, generated at runtime. Default logging level is set to INFO, but one can ```export DEBUG="true"``` to change it to DEBUG (thus, a lot more API I/O data will be shown, thanks to the calls of method such as ```Requests.log_summary()```).

All tests should be in classes inheriting from ApiTestBase (tests/test_base.py) or SeleniumTestBase (tests/test_base_selenium.py).

A test should always start with the prefix "test_" (so pytest can find it) and have a Docstring with its description. Later, this description will be shown together with the test name and status in the HTML report ```pytest-results.html```. After each test(s) execution, the JUnit friendly ```pytest-results.xml``` is also generated.

In order to allow multiple checks in a same test, all tests should end with a call to ```ApiTestBase.then_everything_should_be_fine``` - this method checks if error messages where added or not and call an assert to finish the test. 

Therefore, a test should add error messages with ```ApiTestBase.add_fail_message``` or ```ApiTestBase.add_fail_messages```. When an API request happens, some automatic checks are done (to guarantee the response status code was as expected, for example). Therefore, the test is free to manipulate these messages in ```ApiBase.error_messages``` and flush it to his own area of error messages with ```ApiTestBase.flush_api_messages```.

As an HTML report is generated in the end, a test can decide to add more status messages to it by using ```ApiTestBase.add_output_message``` or ```ApiTestBase.add_output_messages```.

### API test tips:

When a test calls an API and grab an object, it's often useful to check if it contains the proper name or description. It can be achieved via the class ```EqualsDeep``` as follows:

```python
api = ApiGitlab(self.environment.GITLAB_BASE, self.environment.GITLAB_KEY)
project: GitlabProject = api.search_project("gpaoliveira_playground")
equals = EqualDeep()
if not equals.run(target=project, name="gpaoliveira_playground"):
    self.add_fail_messages(equals.error_messages)
```

Additionally, ```EqualsDeep.two_objects``` can be called to compare the public attributes (the ones that do not starts with an underscore) of these objects. It can be used as follows:

```python
equals = EqualDeep()
if not equals.two_objects(issue, retrieved_issue):
    self.then_everything_should_be_fine(
        ["issue created != retrieved - {}".format(",".join(equals.error_messages))]
)
else:
    self.add_output_message("issue created == retrieved")
```

Furthermore, comparing two objects may be useful when loading a list of serialized objects to a JSON file. Test should save such files using ```ApiTestBase.data_test_file_path```. To save a list of objects, use ```JsonFile.list_to_json_file```. To load them again, use ```JsonFile.parse_from_json_file```.

### API Classes tips

APIs classes are all based on Requests (framework/requests/requests.py), a custom based Facade to the Python's request library and urllopen library that allow us to simplify the steps needed for a request to be made, regardless of content type. One client needs only to instantiate Requests with parameters, call ```request()``` and interact with the attributes generated. Clients can also use ```save()```  to write Requests data to the filesystem (generating two JSONs, one with the Object attributes serialized and another with the response payload). Finally, a summary can be logged with ```log_summary()```. All these methods are used by ApiBase and encapsulated on ```request()``` - thus, children only need to call ```ApiBase.request``` to perform GETs/POSTs/etc. If schema valdation is import, children can also call ```ApiBase.validate_json_schema``` with a json schema filename. The saved files generated by ```Requests.save``` call are not being saved on CircleCI as artifacts, to avoid APIs private information to be showed.

In order to allow the test cases the flexibility needed, force all API methods to return a Data Object (or None, or [], in error scenarios). In that way, these Data objects can be verified by the test case or other classes.

### Page Object tips

UI Page Objects (inherited from framework/pages/page_base.py) are classes that drive a Browser (a class from from framework/pages/page_base.py), instantiated by SeleniumTestBase (tests/test_base_selenium.py), to allow the test cases to fulfill tasks on the Browser UI.

The Browser object has methods common to all POs, such as ```set_timeout``` (to modify the implicit wait for all elements), ```save_screenshot``` (to save a snapshot of the current browser, useful in error situations), and ```save_html``` (to save the current browser HTML, useful in error situations). 

The PageBase object (framework.pages.page_base.PageBase) is the one to be inherited by all POs, as it carries proper helpers to interact with Browser or Element. For example, when an exception occurs, the method ```PageBase.exception_to_error_message``` takes care of the burden to save a snapshot and the page html and to put the exception message on error_messages. 

A class inheriting from PageBase need also to provide an instance of LocatorsBase (framework.pages.page_base.LocatorsBase) as input. A LocatorsBase children should define constants (such as below) with locators to be used to generate Elements.

```python
class LocatorsSignUpMain(LocatorsBase):
    DESKTOP_HEADER = (By.TAG_NAME, 'desktop-page-header')
    SIGNUP_BUTTON = (By.CLASS_NAME, 'e2e-signup-link')
```

Every locator defined like that will be used by PageBase to generate a Element (framework.pages.page_base.Element) instance and store it in a dynamically created attribute with the locator name. For example, the PageSignUpMain that was created using the LocatorsSignUpMain above can use ```self.SIGNUP_BUTTON``` when needed.

```python
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

```

As exemplified above, whenever a click carries the user over to a new page, we need to force a new set of selectors to be loaded. This can either be achieved by calling ```PageBase.load_new_page(new_page_class_to_instantiate_and_load)``` method or by ```PageBase.load(new_locators_base_instance)```. 

