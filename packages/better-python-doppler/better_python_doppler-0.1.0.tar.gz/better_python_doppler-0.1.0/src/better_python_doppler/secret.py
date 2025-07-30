from __future__ import annotations
from typing import Literal

from requests import Response

from better_python_doppler.models import SecretModel, SecretValue
from better_python_doppler.apis import SecretAPI

class Secrets:

    def __init__(
            self,
            service_token: str
        ) -> None:
        
        self._service_token = service_token
    
    def list(
        self,
        project_name: str,
        config_name: str,
        include_dynamic_secrets: bool = True,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] | None = None,
        include_managed_secrets: bool = True,
    ) -> list[SecretModel]:
        response = SecretAPI.list_secrets(
            auth=self._service_token,
            project_name=project_name,
            config_name=config_name,
            include_dynamic_secrets=include_dynamic_secrets,
            dynamic_secrets_ttl_sec=dynamic_secrets_ttl_sec,
            secrets=secrets,
            include_managed_secrets=include_managed_secrets,
        )
        response.raise_for_status()
        data = response.json()

        secrets_dict = data.get("secrets", {})
        secret_models = []
        for name, value_dict in secrets_dict.items():
            secret_value = SecretValue(
                raw=value_dict.get("raw"),
                computed=value_dict.get("computed"),
                note=value_dict.get("note"),
            )
            secret_model = SecretModel(name=name, value=secret_value)
            secret_models.append(secret_model)
        return secret_models

    def list_names(
        self,
        project_name: str,
        config_name: str,
        include_dynamic_secrets: bool = False,
        include_managed_secrets: bool = True,
    ) -> list[str]:
        response = SecretAPI.list_secret_names(
            auth=self._service_token,
            project_name=project_name,
            config_name=config_name,
            include_dynamic_secrets=include_dynamic_secrets,
            include_managed_secrets=include_managed_secrets,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("names", [])

    def get(self, project_name: str, config_name: str, secret_name: str) -> SecretModel:
        response = SecretAPI.get_secret(
            auth=self._service_token,
            project_name=project_name,
            config_name=config_name,
            secret_name=secret_name,
        )
        return response_to_model(response)

    def update(
        self, project_name: str, config_name: str, secrets: dict[str, str]
    ) -> list[SecretModel]:
        response = SecretAPI.update_secrets(
            auth=self._service_token,
            project_name=project_name,
            config_name=config_name,
            secrets=secrets,
        )
        response.raise_for_status()
        data = response.json()

        secrets_dict = data.get("secrets", {})
        secret_models = []
        for name, value_dict in secrets_dict.items():
            secret_value = SecretValue(
                raw=value_dict.get("raw"),
                computed=value_dict.get("computed"),
                note=value_dict.get("note"),
            )
            secret_model = SecretModel(name=name, value=secret_value)
            secret_models.append(secret_model)
        return secret_models
    
    def download(
        self,
        project_name: str,
        config_name: str,
        format: Literal["json", "dotnet-json", "env", "yaml", "docker", "env-no-quotes"] = "json",
        name_transformer: Literal["camel", "upper-camel", "lower-snake", "tf-var", "dotnet", "dotnet-env", "lower-kebab"] | None = None,
        include_dynamic_secrets: bool = False,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] | None = None,
    ) -> dict[str, str] | str:
        response = SecretAPI.download_secrets(
            auth=self._service_token,
            project_name=project_name,
            config_name=config_name,
            format=format,
            name_transformer=name_transformer,
            include_dynamic_secrets=include_dynamic_secrets,
            dynamic_secrets_ttl_sec=dynamic_secrets_ttl_sec,
            secrets=secrets or [],
        )
        response.raise_for_status()
        if format in ["json", "dotnet-json"]:
            return response.json()
        return response.text
    
    def delete(self, project_name: str, config_name: str, secret_name: str) -> None:
        response = SecretAPI.delete_secret(
            auth=self._service_token,
            project_name=project_name,
            config_name=config_name,
            secret_name=secret_name,
        )
        response.raise_for_status()
    
    def update_note(self, project_name: str, secret_name: str, note: str) -> dict:
        response = SecretAPI.update_note(
            auth=self._service_token,
            project_name=project_name,
            secret_name=secret_name,
            note=note,
        )
        response.raise_for_status()
        return response.json()
    
def response_to_model(response: Response) -> SecretModel:
    response.raise_for_status()
    data = response.json()

    value_dict = data.get("value", {})
    secret_value = SecretValue(
        raw=value_dict.get("raw"),
        computed=value_dict.get("computed"),
        note=value_dict.get("note"),
    )

    return SecretModel(name=data.get("name"), value=secret_value)
