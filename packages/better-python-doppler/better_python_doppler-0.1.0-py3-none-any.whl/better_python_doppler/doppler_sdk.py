# src\better_python_doppler\doppler_sdk.py

from better_python_doppler.secret import Secrets

class Doppler:

    def __init__(
            self,
            service_token: str | None = None,
            *,
            service_token_environ_name: str | None = None
        ) -> None:

        self._service_token = self._get_service_token(service_token, service_token_environ_name)
        
        self._secrets: Secrets | None = None 


    def _get_service_token(
            self, 
            service_token: str | None = None,
            service_token_environ_name: str | None = None
        ) -> str:

        if (service_token is None) == (service_token_environ_name is None):
            raise ValueError("Either `service_token` OR `service_token_environ_name` must be provided upon init. NOT both or neither.") 
        
        if service_token is not None:
            return service_token
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()

            pulled_token = os.getenv(service_token_environ_name) # type: ignore

            if pulled_token is None:
                raise ValueError("Attempting to retrieve the environmental variable named `%s` returns `None`.", service_token_environ_name)    

            return pulled_token
        
    @property
    def service_token(self) -> str:
        return self._service_token
    
    @property
    def Secrets(self) -> Secrets:
        if self._secrets is None:
            self._secrets = Secrets(self._service_token)

        return self._secrets
    
    
    