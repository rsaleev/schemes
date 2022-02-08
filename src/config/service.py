
from typing import Dict, List, Any, Optional
from pydantic import BaseSettings, validator

""""
https://pydantic-docs.helpmanual.io/usage/settings/
"""

class Settings(BaseSettings):

    fastapi_app_debug: bool = False
    fastapi_app_title:Optional[str] = 'Схемы документов'
    fastapi_app_version:Optional[str] = '0.1.1'
    fastapi_app_author:Dict[str, str] = {'author':'Rostislav Aleev', 'mail':'rs.aleev@gmail.com'}
    cors_allow_methods: Optional[List[str]] = ["POST", "DELETE", "GET", "PUT"]
    cors_allow_origins: Optional[List[str]] = ["*"]
    cors_allow_credentials: Optional[bool] = True
    cors_allow_headers: Optional[List[str]]= ["*"]

    class Config:

        @classmethod
        def customise_sources(
            cls,
            env_settings,
            init_settings,
            file_secret_settings,
        ):
            return (
                env_settings,
                init_settings,
                file_secret_settings
            )
