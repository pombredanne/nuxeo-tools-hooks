# coding=UTF-8

import json

from github.MainClass import Github
from github.GithubException import UnknownObjectException
from nxtools import services
from nxtools.hooks.endpoints.webhook import AbstractWebHook
from nxtools.hooks.entities.github_entities import OrganizationWrapper
from nxtools.hooks.services.config import Config


class UnknownEventException(Exception):
    def __init__(self, event):
        super(UnknownEventException, self).__init__("Unknown event '%s'" % event)


class InvalidPayloadException(Exception):
    def __init__(self, previous):
        self.previous = previous

        super(InvalidPayloadException, self).__init__()


class NoSuchOrganizationException(Exception):
    def __init__(self, organization):
        super(NoSuchOrganizationException, self).__init__("Unknown organization '%s'" % organization)


class GithubHook(AbstractWebHook):

    eventSource = "Github"
    payloadHeader = "X-GitHub-Event"
    github_events = {}

    _handlers = {}
    """:type : dict[str, list[AbstractGithubHandler]]"""

    def __init__(self):
        self._organizations = {}

        # TODO: https://github.com/organizations/nuxeo-sandbox/settings/applications
        self.github = Github("")

    def can_handle(self, headers, body):
        return GithubHook.payloadHeader in headers

    @property
    def config(self):
        """
        :rtype: nxtools.hooks.services.config.Config
        """
        return services.get(Config)

    @staticmethod
    def add_handler(event, handler):
        """
        @type event : str
        @type handler : nxtools.hooks.endpoints.github_hook.AbstractGithubHandler
        """
        if event not in GithubHook._handlers:
            GithubHook._handlers[event] = [handler]
        else:
            GithubHook._handlers[event].append(handler)

    @staticmethod
    def get_handlers(event):
        """
        :rtype: list[nxtools.hooks.endpoints.github_hook.AbstractGithubHandler]
        @type event : str
        """
        return GithubHook._handlers[event] if event in GithubHook._handlers else []

    def get_organization(self, name):
        """
        :rtype: nxtools.hooks.entities.github_entities.OrganizationWrapper
        """
        if name not in self._organizations:
            try:
                self._organizations[name] = OrganizationWrapper(self.github.get_organization(name))
            except UnknownObjectException:
                raise NoSuchOrganizationException(name)
        return self._organizations[name]

    def handle(self, headers, body):
        """
        @type headers : dict[str, str]
        @type body : str
        """

        if GithubHook.payloadHeader in headers:
            payload_event = headers[GithubHook.payloadHeader]
            handlers = GithubHook.get_handlers(payload_event)

            if handlers:
                json_body = json.loads(body)

                for handler in handlers:
                    handler.handle(json_body)
            else:
                raise UnknownEventException(payload_event)