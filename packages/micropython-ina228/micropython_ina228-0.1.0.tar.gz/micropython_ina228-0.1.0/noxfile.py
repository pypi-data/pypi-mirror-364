# Copyright 2024 - 2025 Avram Lubkin, All Rights Reserved

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Nox configuration file
See https://nox.thea.codes/en/stable/config.html
"""

import nox

try:
    # Python >= 3.11
    import tomllib as toml
except ImportError:
    # Included with Nox for Python <= 3.11
    import tomli as toml

BASE_PYTHON = '3.13'

with open('pyproject.toml', 'rb') as toml_file:
    CONFIG = toml.load(toml_file)

NOX_DEPENDENCIES = ('nox',)


@nox.session(python=BASE_PYTHON, tags=['lint'])
def pylint(session: nox.Session) -> None:
    """Run Pylint"""
    session.install('pylint[spelling]', *NOX_DEPENDENCIES)
    session.run('pylint', '*.py')


@nox.session(python=BASE_PYTHON, tags=['lint'])
def flake8(session: nox.Session) -> None:
    """Run Flake8"""
    session.install('flake8', 'Flake8-pyproject')
    session.run('python', '-m', 'flake8')


@nox.session(python=BASE_PYTHON, tags=['lint'])
def mypy(session: nox.Session) -> None:
    """Run mypy"""
    session.install('mypy', 'micropython-esp32-esp32_generic-stubs')
    session.run('mypy', 'ina228.py')
