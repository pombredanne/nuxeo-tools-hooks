"""
(C) Copyright 2016 Nuxeo SA (http://nuxeo.com/) and contributors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
you may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contributors:
    Pierre-Gildas MILLON <pgmillon@nuxeo.com>
"""

import json
import os

from mock.mock import PropertyMock
from nxtools import services
from nxtools.hooks.endpoints.webhook.github_hook import GithubHook
from nxtools.hooks.services.config import Config
from nxtools.hooks.tests.webhooks import WebHooksTestCase


class GithubHookHandlerTest(WebHooksTestCase):

    class payload_file(object):

        def __init__(self, filename):
            self.filename = filename
            self.payload_file = None
            self.headers_file = None

        def __enter__(self):
            self.payload_file = open('nxtools/hooks/tests/resources/github_handlers/%s.json' % self.filename)
            self.headers_file = open('nxtools/hooks/tests/resources/github_handlers/%s.headers.json' % self.filename)
            return self.payload_file.read(), json.load(self.headers_file)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.payload_file.close()
            self.headers_file.close()

    def get_json_body_from_payload(self, payload):
        raw_body, headers = payload
        return json.loads(raw_body)

    def setUp(self):
        super(GithubHookHandlerTest, self).setUp()

        os.environ[Config.ENV_PREFIX + Config.CONFIG_FILE_KEY] = \
            'nxtools/hooks/tests/resources/github_handlers/config.ini'
        services.get(Config).reload()

        self.hook = services.get(GithubHook)

        self.maxDiff = None

        # Mocks required for nxtools.hooks.entities.github_entities.RepositoryWrapper#get_commit_diff
        self.mocks.repository_url = PropertyMock(return_value="http://null.void/")
        type(self.mocks.organization.get_repo.return_value).url = self.mocks.repository_url
        self.mocks.requester.requestJsonAndCheck.return_value = ({}, {'data': "Query mocked"})
        self.mocks.organization.get_repo.return_value._requester = self.mocks.requester
