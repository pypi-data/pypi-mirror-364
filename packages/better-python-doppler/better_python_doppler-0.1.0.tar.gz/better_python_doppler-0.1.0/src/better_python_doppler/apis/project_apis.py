# src\better_python_doppler\apis\project_apis.py

import requests
from requests import Response

class ProjectAPI:
    
    @staticmethod
    def list_projects(
            auth: str, 
            page: int = 1, 
            per_page: int = 20
        ) -> Response:

        base_url = "https://api.doppler.com/v3/projects"
        params = {
            "page":     page,
            "per_page": per_page
            }
        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }

        return requests.get(base_url, params, headers=headers)
    @staticmethod
    def get_project(
            auth: str, 
            project_name: str
        ) -> Response:

        base_url = "https://api.doppler.com/v3/projects/project"
        params = {
            "project": project_name
            }

        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }

        return requests.get(base_url, params, headers=headers)