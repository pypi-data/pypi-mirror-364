# o7-util
O7 Python library of useful &amp; common modules


## Dev Notes

lint code: `pylint src`
Reformat to Black: `black src`
Unit Test: `pytest`
Unit Test + Coverage: `pytest --cov=o7util --cov-report=term --cov-report=html --cov-branch tests/test_color.py`

### Set up git hooks
Very useful to apply formatting and make lint checks before commits
- Run : `git config --local core.hooksPath .githooks/`

## Semantic Release
Ref: https://python-semantic-release.readthedocs.io/en/latest/

- Test : `semantic-release --noop version`
- Real : `semantic-release version`

## Commit Message Convention

Commit Message Header `<type>(<scope>): <short summary>`

### Possible Type:
- build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- ci: Changes to our CI configuration files and scripts (examples: CircleCi, SauceLabs)
- docs: Documentation only changes
- feat: A new feature
- fix: A bug fix
- perf: A code change that improves performance
- refactor: A code change that neither fixes a bug nor adds a feature
- test: Adding missing tests or correcting existing tests

Ref: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format



## Regenerate requirements.txt
``` bash
pip install pip-tools
pip-compile pyproject.toml
```