# src\better_python_doppler\apis\config_apis.py

import requests
from requests import Response
from urllib.parse import quote as url_encode

class ConfigAPI:

    @staticmethod
    def list_configs(
            auth: str, 
            project_name: str, 
            environment_slug: str = "Environment slug", 
            page: int = 1, 
            per_page: int = 20
        ) -> Response:

        base_url = "https://api.doppler.com/v3/configs"
        params = {
            "project":      project_name,
            "environment":  url_encode(environment_slug),
            "page":         page,
            "per_page":     per_page
            }

        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }

        return requests.get(base_url, params, headers=headers)

    @staticmethod
    def get_config(
            auth: str, 
            project_name: str, 
            config_name: str
        ) -> Response:
        
        base_url = "https://api.doppler.com/v3/configs/config"
        params = {
            "project": project_name,
            "config":  config_name
            }

        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }

        return requests.get(base_url, params, headers=headers)