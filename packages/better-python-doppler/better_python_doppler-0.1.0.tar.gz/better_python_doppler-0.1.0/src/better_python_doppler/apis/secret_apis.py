# src\better_python_doppler\apis\secret_apis.py

import requests
from requests import Response
from typing import Literal

class SecretAPI:

    @staticmethod
    def list_secrets(
        auth: str,
        project_name: str,
        config_name: str,
        include_dynamic_secrets: bool = True,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] | None = None,
        include_managed_secrets: bool = True
    ) -> Response:
        base_url = "https://api.doppler.com/v3/configs/config/secrets"
        params = {
            "project":  project_name,
            "config":   config_name,
            "include_dynamic_secrets": str(include_dynamic_secrets).lower(),
            "dynamic_secrets_ttl_sec": dynamic_secrets_ttl_sec,
            "include_managed_secrets": str(include_managed_secrets).lower(),
            }
        
        headers = {
            "Accept":           "application/json",
            "Authorization":    f"Bearer {auth}",
            }
        
        if secrets:
            params["secrets"] = ",".join(secrets)

        return requests.get(base_url, params, headers=headers)

    @staticmethod
    def list_secret_names(
            auth: str, 
            project_name: str, 
            config_name: str, 
            include_dynamic_secrets: bool = False, 
            include_managed_secrets: bool = True
        ) -> Response:

        base_url = "https://api.doppler.com/v3/configs/config/secrets/names"
        params = {
            "project":  project_name,
            "config":   config_name,
            "include_dynamic_secrets":  str(include_dynamic_secrets).lower(),
            "include_managed_secrets":  str(include_managed_secrets).lower(),
            }
        
        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
            }
        
        return requests.get(base_url, params, headers=headers)

    @staticmethod
    def get_secret(
            auth: str, 
            project_name: str, 
            config_name: str,
            secret_name: str 
        ) -> Response:
        base_url = "https://api.doppler.com/v3/configs/config/secret"
        params = {
            "project":  project_name,
            "config":   config_name,
            "name":     secret_name
            }

        headers = {
            "accept":           "application/json",
            "authorization":    f"Bearer {auth}"
        }

        return requests.get(base_url, params, headers=headers)

    @staticmethod
    def update_secrets(
            auth: str, 
            project_name: str, 
            config_name: str, 
            secrets: dict[str, str]
        ) -> Response:
        base_url = "https://api.doppler.com/v3/configs/config/secrets"

        payload = {
            "project":  project_name,
            "config":   config_name,
            "secrets":  secrets
        }

        headers = {
            "accept":           "application/json",
            "content-type":     "application/json",
            "authorization":    f"Bearer {auth}"
        }

        return requests.post(base_url, headers=headers, json=payload)

    @staticmethod
    def download_secrets(
            auth: str, 
            project_name: str, 
            config_name: str,
            format: Literal["json", "dotnet-json", "env", "yaml" , "docker", "env-no-quotes"] = "json",
            name_transformer: Literal["camel", "upper-camel", "lower-snake", "tf-var", "dotnet", "dotnet-env", "lower-kebab"] | None = None,
            include_dynamic_secrets: bool = False,
            dynamic_secrets_ttl_sec: int = 1800,
            secrets: list[str] = []
        ) -> Response:

        base_url = "https://api.doppler.com/v3/configs/config/secrets/download"
        params = {
            "project":  project_name,
            "config":   config_name,
            "format":   format,
            "include_dynamic_secrets" : str(include_dynamic_secrets).lower(),
            "dynamic_secrets_ttl_sec" : str(dynamic_secrets_ttl_sec).lower(),
        }

        if name_transformer:
            params["name_transformer"] = name_transformer
        if secrets:
            params["secrets"] = ",".join(secrets)

        accept_header = "application/json"
        if format not in ["json", "dotnet-json"]:
            accept_header = "text/plain"

        headers = {
            "accept": accept_header,
            "authorization": f"Bearer {auth}"
        }

        return requests.get(base_url, params, headers=headers)

    @staticmethod
    def delete_secret(
            auth: str, 
            project_name: str, 
            config_name: str, 
            secret_name: str
        ) -> Response:
        base_url = "https://api.doppler.com/v3/configs/config/secret"
        params = {
            "project":  project_name,
            "config":   config_name,
            "name":     secret_name
        }

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {auth}"
        }

        return requests.delete(base_url, params=params, headers=headers)

    @staticmethod   
    def update_note(
            auth: str, 
            project_name: str, 
            secret_name: str,
            note: str 
        ) -> Response:

        base_url = "https://api.doppler.com/v3/projects/project/note"
        params = {
            "project": project_name
        }

        payload = {
            "secret": secret_name,
            "note": note
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {auth}"
        }

        return requests.post(base_url, params=params, headers=headers, json=payload)
