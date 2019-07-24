import pytest
import os
import json
from datetime import datetime
import re
from py.xml import html, raw
from lxml import html as lxmlhtml
from pytest_html import extras
import pdb

PYTEST_ENVIRONMENT_JSON = "pytest-results.environment.json"


def pytest_configure(config):
    config._metadata.pop('Packages')
    config._metadata.pop('Plugins')
    if "TEST_FILE" is os.environ:
        config._metadata["TEST_FILE"] = os.environ["TEST_FILE"]
    if "TEST_TAG" is os.environ:
        config._metadata["TEST_TAG"] = os.environ["TEST_TAG"]
    config.option.disable_warnings = True


def pytest_addoption(parser):
    pass


def pytest_runtest_setup(item):
    pass


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    """ Called after building results table header. """
    cells.insert(2, html.th('Description'))
    cells.insert(0, html.th('Time', class_='sortable time', col='time'))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    """ Called after building results table row. """
    try:
        test_steps = [step for step in re.split('\n *', report.description) if len(step) > 0]
        html_test_steps = list(map(lambda step: html.p(step), test_steps))
        test_file_path, test_class, test_name = re.search('>(.*)<', str(cells[1])).groups()[0].split("::")
        cells[1] = html.td(test_name, class_='col-name')
        cells.insert(2, html.td(html_test_steps))
        cells.insert(0, html.td(datetime.utcnow(), class_='col-time'))
        cells.pop()
    except Exception as e:
        pass


@pytest.mark.optionalhook
def pytest_html_results_table_html(report, data):
    if report.failed:
        # Extract important lines
        failure_lines = [
            line
            for line in lxmlhtml.fromstring(str(data[-1])).xpath('//div/text()')
            if line.startswith(">")
            or " def " in line
        ]
        error_spans = [
            str(html.span("* " + line[1:].lstrip().rstrip(), class_='error'))
            for line in lxmlhtml.fromstring(str(data[-1])).xpath('//span/text()')
            if "Fail Message(s) for test" not in line
        ]
        # Reconstruct error log
        # Taken from append_log_html in https://github.com/pytest-dev/pytest-html/blob/master/pytest_html/plugin.py
        del data[-1]
        log = html.div(class_='log')
        for line in failure_lines:
            log.append(raw(line))
            log.append(html.br())
        for line in error_spans:
            log.append(html.span(raw(line), class_='error'))
            log.append(html.br())
        data.append(log)
    elif report.passed:
        del data[1]


def get_verification_block_from_log_lines(log_path):
    with open(log_path) as log:
        lines = log.readlines()
        verification_start = [l for l in lines if "verification points:" in l][0]
        verification_end = [l for l in lines if "Fail Message(s)" in l][0]
        verification_lines_to_add = lines[lines.index(verification_start):lines.index(verification_end)]
    return verification_lines_to_add


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    extra = getattr(report, 'extra', [])
    if report.when == 'call':
        # Grab test customized output (a custom variable tests can populate if needed
        test_reporter_keys = [k for k in item.config._xml.node_reporters.keys() if k[0] == item.nodeid]
        node_reporter = item.config._xml.node_reporters[test_reporter_keys[0]]
        pytest_output = item._testcase._pytest_output if "_pytest_output" in dir(item._testcase) else ""
        item.config._metadata = None

        # put in the HTML report
        extra.append(extras.html("<div class=\"log\">{}</div>".format(pytest_output)))
        report.extra = extra

        # put in the JUnit XML - our jira script will replace the \\n back
        node_reporter.add_property("pytest_output", pytest_output.replace("\n", "\\n"))

