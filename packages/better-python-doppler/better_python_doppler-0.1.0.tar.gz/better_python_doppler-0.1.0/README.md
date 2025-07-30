# Better Python Doppler

Better Python Doppler is a lightweight SDK around the [Doppler API](https://docs.doppler.com/reference). It wraps common API endpoints in simple Python classes and includes typed models for working with secrets.

## Installation

This project currently requires Python 3.12 or newer. Once published to PyPI it can be installed with `pip`:

```bash
pip install better-python-doppler
```

For local development clone the repository and install the dependencies:

```bash
pip install -e .
```

## Quick Start

The example below mirrors `examples/example_secrets.py` and demonstrates basic usage of the SDK. It assumes the environment variables `SERVICE_TOKEN`, `PROJECT_NAME`, `CONFIG_NAME` and `SECRET_NAME` are available.

```python
from better_python_doppler import Doppler

# Create the SDK instance
sdk = Doppler(service_token=os.getenv("SERVICE_TOKEN"))

# List secret names
names = sdk.Secrets.list_names(
    project_name=os.getenv("PROJECT_NAME"),
    config_name=os.getenv("CONFIG_NAME")
)

# Fetch all secrets
secrets = sdk.Secrets.list(
    project_name=os.getenv("PROJECT_NAME"),
    config_name=os.getenv("CONFIG_NAME")
)

# Retrieve a specific secret value
secret_value = sdk.Secrets.get(
    os.getenv("PROJECT_NAME"),
    os.getenv("CONFIG_NAME"),
    os.getenv("SECRET_NAME")
)
print(secret_value.value.raw)
```

## Functionality

The SDK focuses on secrets management via the `Doppler.Secrets` interface defined in `secret.py`. Supported operations include:

- `list` – return detailed information for all secrets in a config.
- `list_names` – fetch only the secret names.
- `get` – retrieve a single secret as a `SecretModel`.
- `update` – update one or more secret values.
- `download` – download secrets in various formats (json, env, yaml, etc.).
- `delete` – delete a secret.
- `update_note` – modify the note on an existing secret.

Under the hood these call lightweight API wrappers located in `src/better_python_doppler/apis`. The project also exposes minimal data models in `src/better_python_doppler/models` such as `SecretModel` and `SecretValue` for convenient type checking.

Authentication is performed with a Doppler service token. You can pass the token directly when creating `Doppler` or load it from an environment variable using the `service_token_environ_name` parameter.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.