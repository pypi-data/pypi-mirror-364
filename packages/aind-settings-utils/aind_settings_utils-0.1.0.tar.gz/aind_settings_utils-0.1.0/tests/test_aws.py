"""Module to test custom settings"""

import os
import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from aind_settings_utils.aws import (
    AWSParamStoreAppSource,
    ParameterStoreAppBaseSettings,
    SecretsManagerBaseSettings,
)


class ExampleSettings(ParameterStoreAppBaseSettings):
    """Example settings class for testing"""

    my_secret: str

    model_config = {
        "aws_param_store_name": "example-name",
        "case_sensitive": False,
    }


class ExampleSettingsForSecretsManager(SecretsManagerBaseSettings):
    """Example settings class for testing"""

    my_param_1: str
    my_param_2: int


class TestAWSParamStoreSource(unittest.TestCase):
    """Test AWSParamStoreAppSource class"""

    @patch("aind_settings_utils.aws.boto3.client")
    def test_get_parameter(self, mock_boto_client: MagicMock):
        """Tests that parameter is retrieved as expected"""
        # Mock response
        mock_ssm = MagicMock()
        mock_ssm.get_parameter.return_value = {
            "Parameter": {"Value": '{"my_secret": "secret_value"}'}
        }
        mock_boto_client.return_value = mock_ssm

        result = AWSParamStoreAppSource._get_parameter("example-name")
        self.assertEqual(result, {"my_secret": "secret_value"})
        mock_ssm.get_parameter.assert_called_once_with(
            Name="example-name", WithDecryption=True
        )
        mock_ssm.close.assert_called_once()

    def test_find_case_param(self):
        """Tests that correct parameter is found in json dictionary"""

        json_contents = {"keyOne": "value1", "KEYTWO": "value2"}
        result1 = AWSParamStoreAppSource.find_case_param(
            json_contents, "keyOne", case_sensitive=False
        )
        result2 = AWSParamStoreAppSource.find_case_param(
            json_contents, "keytwo", case_sensitive=False
        )
        result3 = AWSParamStoreAppSource.find_case_param(
            json_contents, "keytwo", case_sensitive=True
        )

        self.assertEqual(result1, "value1")
        self.assertEqual(result2, "value2")
        self.assertIsNone(result3)

    @patch("aind_settings_utils.aws.boto3.client")
    def test_get_field_value_success(self, mock_boto_client: MagicMock):
        """Tests that field value is retrieved successfully"""

        mock_ssm = MagicMock()
        mock_ssm.get_parameter.return_value = {
            "Parameter": {"Value": '{"MY_SECRET": "top_secret"}'}
        }
        mock_boto_client.return_value = mock_ssm
        source = AWSParamStoreAppSource(
            ExampleSettings, aws_param_store_name="example-store-name"
        )
        field = ExampleSettings.model_fields["my_secret"]

        value, key, is_complex = source.get_field_value(field, "my_secret")
        self.assertEqual(value, "top_secret")
        self.assertEqual(key, "my_secret")
        self.assertFalse(is_complex)

    @patch.object(
        AWSParamStoreAppSource, "_json_contents", new_callable=PropertyMock
    )
    def test_get_field_value_failure(self, mock_json_contents: MagicMock):
        """Tests that field value is not retrieved successfully"""

        mock_json_contents.return_value = {}
        source = AWSParamStoreAppSource(
            ExampleSettings, aws_param_store_name="example-store-name"
        )
        field = ExampleSettings.model_fields["my_secret"]

        value, key, is_complex = source.get_field_value(field, "my_secret")
        self.assertIsNone(value)
        self.assertEqual(key, "my_secret")
        self.assertFalse(is_complex)


class TestParameterStoreAppBaseSettings(unittest.TestCase):
    """Test ParameterStoreBaseSettings class"""

    def test_settings_customise_sources_with_param_store(self):
        """Tests that sources are customised correctly"""
        init = MagicMock()
        env = MagicMock()
        dotenv = MagicMock()
        secret = MagicMock()
        sources = ParameterStoreAppBaseSettings.settings_customise_sources(
            settings_cls=ExampleSettings,
            init_settings=init,
            env_settings=env,
            dotenv_settings=dotenv,
            file_secret_settings=secret,
        )
        self.assertIsInstance(sources[1], AWSParamStoreAppSource)

    def test_settings_customise_sources_without_param_store(self):
        """Tests that sources are customised correctly"""

        class NoParamSettings(ParameterStoreAppBaseSettings):
            """Example settings class for testing no param store"""

            model_config = {}

        init = MagicMock()
        env = MagicMock()
        dotenv = MagicMock()
        secret = MagicMock()

        sources = NoParamSettings.settings_customise_sources(
            NoParamSettings, init, env, dotenv, secret
        )
        self.assertEqual(sources[0], init)
        self.assertEqual(len(sources), 4)


class TestSecretsManagerBaseSettings(unittest.TestCase):
    """Test SecretsManagerBaseSettings class"""

    @patch.dict(
        os.environ,
        dict(),
        clear=True,
    )
    @patch("boto3.client")
    def test_settings_no_secrets_manager(self, mock_boto: MagicMock):
        """Tests settings with no secret manager id"""
        settings = ExampleSettingsForSecretsManager(
            my_param_1="a", my_param_2=1
        )
        mock_boto.assert_not_called()
        self.assertIsNotNone(settings)

    @patch.dict(
        os.environ,
        {
            "AWS_SECRETS_MANAGER_SECRET_ID": "abc/def",
            "AWS_REGION": "us-west-2",
        },
        clear=True,
    )
    @patch("boto3.client")
    def test_settings_with_secrets_manager(self, mock_boto: MagicMock):
        """Tests settings with no secret manager id"""

        mock_sm = MagicMock()
        mock_sm.get_secret_value.return_value = {
            "SecretString": '{"MY_PARAM_1":"a","MY_PARAM_2":"1"}'
        }
        mock_boto.return_value = mock_sm

        settings = ExampleSettingsForSecretsManager()
        expected_settings = ExampleSettingsForSecretsManager(
            my_param_1="a", my_param_2=1
        )
        self.assertEqual(settings, expected_settings)


if __name__ == "__main__":
    unittest.main()
