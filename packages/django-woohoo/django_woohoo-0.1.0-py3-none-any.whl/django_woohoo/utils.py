import os
from ast import literal_eval
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(setting, default=None):
    """
    Returns the variable value from a `.env` file or system environment.

    Args:
        setting (str): Environment variable name.
        default: Fallback value if not found.

    Raises:
        ImproperlyConfigured: If variable is missing and no default is provided.
    """
    def _load_env_file():
        env_path = Path('.env')
        if not env_path.exists():
            return None

        environ = {}
        with env_path.open() as env_file:
            for line in env_file:
                name, _, value = [c.strip() for c in line.partition('=')]
                if line.startswith('#') or line.isspace() or value is None:
                    continue
                environ[name] = literal_eval(value)
        return environ

    environ = _load_env_file() or os.environ

    try:
        return environ[setting]
    except KeyError:
        if default is not None:
            return default
        raise ImproperlyConfigured(f"Set the {setting} environment variable") from None
