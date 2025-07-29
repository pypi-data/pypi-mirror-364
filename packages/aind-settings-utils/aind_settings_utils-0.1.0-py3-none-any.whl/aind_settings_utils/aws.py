"""Module to handle custom settings pulled from AWS"""

import functools
import json
import logging
import os
from typing import Any, Dict, Optional, Tuple, Type

import boto3
from pydantic.fields import FieldInfo
from pydantic_settings import (
    AWSSecretsManagerSettingsSource,
    BaseSettings,
    PydanticBaseSettingsSource,
)
from pydantic_settings.sources import PydanticBaseEnvSettingsSource


class AWSParamStoreAppSource(PydanticBaseEnvSettingsSource):
    """
    Custom source that will pull settings defined in a json file hosted on
    AWS Parameter Store.
    """

    # noinspection PyUnresolvedReferences
    def __init__(
        self,
        settings_cls: Type[BaseSettings],
        aws_param_store_name: Optional[str] = None,
        case_sensitive: Optional[bool] = None,
        env_prefix: Optional[str] = None,
        env_ignore_empty: Optional[bool] = None,
        env_parse_none_str: Optional[str] = None,
    ) -> None:
        """Class constructor"""
        super().__init__(
            settings_cls,
            case_sensitive,
            env_prefix,
            env_ignore_empty,
            env_parse_none_str,
        )
        self.aws_param_store_name = (
            aws_param_store_name
            if aws_param_store_name is not None
            else self.config.get("aws_param_store_name")
        )

    @staticmethod
    def _get_parameter(parameter_name: str) -> Dict[str, Any]:
        """
        Retrieves a parameter file from AWS Param Store

        Parameters
        ----------
        parameter_name : str
          Parameter name as stored in AWS Param Store

        Returns
        -------
        Dict[str, Any]
          Contents of the secret

        """
        client = boto3.client("ssm")
        try:
            response = client.get_parameter(
                Name=parameter_name, WithDecryption=True
            )
        finally:
            client.close()
        return json.loads(response["Parameter"]["Value"])

    @functools.cached_property
    def _json_contents(self):
        """
        Cache contents to avoid re-downloading.
        """
        contents_from_aws = self._get_parameter(
            self.config.get("aws_param_store_name")
        )
        return contents_from_aws

    @classmethod
    def find_case_param(
        cls, json_contents: dict, param_name: str, case_sensitive: bool
    ) -> Optional[str]:
        """
        Find a parameter from a json dictionary pulled from aws

        Parameters
        ----------
        json_contents: dict
        param_name: str
        case_sensitive: bool
          Whether to search for param name case sensitively.

        Returns
        -------
        str | None
          The parameter pulled from the json object or None if not found.
        """

        if json_contents.get(param_name) is not None:
            return json_contents.get(param_name)
        elif (
            not case_sensitive
            and json_contents.get(param_name.upper()) is not None
        ):
            return json_contents.get(param_name.upper())
        else:
            return None

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """
        Gets the value for field from secret file and a flag to determine
        whether value is complex.

        Parameters
        ----------
        field: FieldInfo
        field_name: str

        Returns
        -------
        Tuple[Any, str, bool]
          A tuple contains the key, value if the file exists otherwise `None`,
          and a flag to determine whether the value is complex.
        """
        param = None
        field_key = ""
        value_is_complex = False
        for field_key, env_name, value_is_complex in self._extract_field_info(
            field, field_name
        ):
            param = self.find_case_param(
                self._json_contents, env_name, self.case_sensitive
            )
            if param:
                return param, field_key, value_is_complex
            else:
                logging.debug(f"param not found {field_key}")

        return param, field_key, value_is_complex


class ParameterStoreAppBaseSettings(BaseSettings):
    """
    Custom Settings class to handle app settings stored as a json file hosted
    on AWS Parameter Store.
    """

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        If the param store name is not set, then use standard fallbacks. If
        param store name is set, then prioritize the values stored there.
        """

        if settings_cls.model_config.get("aws_param_store_name") is None:
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
        else:
            return (
                init_settings,
                AWSParamStoreAppSource(settings_cls),
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )


class SecretsManagerBaseSettings(BaseSettings):
    """Base Settings that will fall back to AWS Secrets Manager."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],  # noqa
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """If env var is not set, then use standard fall backs."""

        secret_manager_id = os.getenv("AWS_SECRETS_MANAGER_SECRET_ID")
        if secret_manager_id:
            aws_secrets_manager_settings = AWSSecretsManagerSettingsSource(
                settings_cls,
                secret_manager_id,
                case_sensitive=False,
                region_name=os.getenv("AWS_REGION"),
            )
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
                aws_secrets_manager_settings,
            )
        else:
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
