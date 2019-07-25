[![CircleCI](https://circleci.com/gh/gpaOliveira/api_tests.svg?style=svg)](https://circleci.com/gh/gpaOliveira/api_tests)

Minimalistic Python 3.6.1 framework to create/run API tests with Pytest, generating a nice HTML and JUnit XML in the end.

Currently supporting:
* Gitlab API (https://docs.gitlab.com/ee/api/README.html)
* Pokemon API (https://pokeapi.co/)

Install with
```bash
setup install
```

Before executing, remember to:
```bash
export GITLAB_KEY="<your-private-key>"
```

Then run tests with:
```bash
pytest tests/
```