# src\better_python_doppler\apis\environment_apis.py

import requests
from requests import Response

class EnvironmentAPI:

    @staticmethod
    def list_environments(
            auth: str, 
            project_name: str
        ) -> Response:

        base_url = "https://api.doppler.com/v3/environments"
        params = {
            "project": project_name
            }

        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }

        return requests.get(base_url, params, headers=headers)

    @staticmethod
    def get_environment(
            auth: str, 
            project_name: str, 
            environment_name: str
        ) -> Response:

        base_url = "https://api.doppler.com/v3/environments/environment"
        params = {
            "project":      project_name,
            "environment":  environment_name
            }

        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }

        return requests.get(base_url, params, headers=headers)