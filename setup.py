import os
from setuptools import setup,find_packages

project_name  =  "ApiTests"
__version__  =  "1.0.0"
__author__  =  "Gabriel Oliveira"
__author_email__  =  "gabriel.pa.oliveira@gmail.com"
__author_username__  =  "gpaOliveira"
__description__  =  "Minimalistic Framework to create/run API tests"

#adapted from https://pythonhosted.org/an_example_pypi_project/setuptools.html
def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        pass
    return ""

setup(
    author = __author__,
    author_email = __author_email__,
    description = __description__,
    install_requires = read("requirements.txt"),
    license = read("LICENSE.md"),
    long_description = read("README.md"),
    name = project_name,
    packages = find_packages(),
    platforms = ["any"],
    setup_requires = ["pytest-runner"],
    tests_require = ["pytest"]
    url = "https://github.com/" + __author_username__ + "/" + project_name,
    version = __version__,
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.6.1',
    ]
)
