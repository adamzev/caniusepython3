# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

import packaging.utils
import requests

import datetime
import json
import logging
import multiprocessing
import pkgutil
import re

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache



try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:  #pragma: no cover
    CPU_COUNT = 2

PROJECT_NAME = re.compile(r'[\w.-]+')
PYPI_INDEX_URL = 'https://pypi.org/pypi'


def just_name(supposed_name):
    """Strip off any versioning or restrictions metadata from a project name."""
    return PROJECT_NAME.match(supposed_name).group(0).lower()


def supports_py3(project_name, index_url=PYPI_INDEX_URL):
    """Check with PyPI if a project supports Python 3."""
    log = logging.getLogger("ciu")
    log.info("Checking {} ...".format(project_name))
    request = requests.get("{}/{}/json".format(index_url, project_name))
    if request.status_code >= 400:
        log = logging.getLogger("ciu")
        log.warning("problem fetching {}, assuming ported ({})".format(
                        project_name, request.status_code))
        return True
    response = request.json()
    return any(c.startswith("Programming Language :: Python :: 3.10")
               for c in response["info"]["classifiers"])
