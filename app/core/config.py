import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "actions-study"
    app_version: str = "0.1.0"
    environment: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", Settings.model_fields["app_name"].default),
        app_version=os.getenv("APP_VERSION", Settings.model_fields["app_version"].default),
        environment=os.getenv("APP_ENV", Settings.model_fields["environment"].default),
    )
