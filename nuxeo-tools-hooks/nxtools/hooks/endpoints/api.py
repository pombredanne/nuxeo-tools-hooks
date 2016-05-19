import json

from flask.blueprints import Blueprint
from nxtools import ServiceContainer, services
from nxtools.hooks.endpoints import AbstractEndpoint
from nxtools.hooks.entities.nuxeo_qa import StoredPullRequest


@ServiceContainer.service
class ApiEndpoint(AbstractEndpoint):

    __blueprint = Blueprint('api', __name__)

    @staticmethod
    def blueprint():
        return ApiEndpoint.__blueprint

    @staticmethod
    @__blueprint.route('/services',)
    def services():
        return json.dumps([t.__module__ + "." + t.__name__ for t, n, v in services.list(object)])

    @staticmethod
    @__blueprint.route('/pull_requests',)
    def list_pull_requests():
        return json.dumps([{
                               "branch": raw_pr.branch,
                               "repository": raw_pr.repository,
                               "head_commit": raw_pr.head_commit
                           } for raw_pr in StoredPullRequest.objects()])

    def get_cors_config(self):
        return {k: v for k, v in self.config.items(self.config_section, {
            "cors_origins": "*"
        }).iteritems() if k.startswith("cors_")}
