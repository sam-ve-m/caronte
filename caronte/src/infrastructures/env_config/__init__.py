import os
import platform
from decouple import Config, RepositoryEnv


def get_config(base_path: str) -> Config:
    path = os.path.join(base_path, "opt", "envs", "caronte.lionx.com.br", ".env")
    path = str(path)
    config = Config(RepositoryEnv(path))
    return config


SYSTEM = platform.system()
supported_systems = {
    "Linux": "/",
    "Darwin": "/",
    "Windows": "C:/",
}

base_path = supported_systems.get(SYSTEM)
config = get_config(base_path)

__all__ = config
