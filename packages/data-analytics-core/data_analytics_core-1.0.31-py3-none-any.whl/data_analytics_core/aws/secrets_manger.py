"""
AWS_SM
Class containing all the needed AWS Secrets Manager actions and the client itself.
"""
import json
from typing import Optional
# custom imports
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface


class AmazonWebServicesSecretsManager(AmazonWebServicesInterface):
    def __init__(self, region_name="eu-central-1"):
        super().__init__(region_name=region_name, service_name="secretsmanager")

    def extract_secret_value_as_str(self, secret_arn_or_name: str) -> Optional[str]:
        return self.client.get_secret_value(SecretId=secret_arn_or_name)["SecretString"]

    def extract_secret_value_as_dict(self, secret_arn_or_name: str) -> Optional[dict]:
        return json.loads(self.client.get_secret_value(SecretId=secret_arn_or_name)['SecretString'])

    def create_secret(self, name: str, secret_value: str, description=Optional[str],
                      kms_key=Optional[str], tags=Optional[list]):
        """
        :param name:
        :param secret_value:
        :param description:
        :param kms_key: This parameter can be the ARN, ID or even the alias given to such key.
        :param tags:
        :return:
        """
        self.client.create_secret(
            Name=name,
            Description=description,
            KmsKeyId=kms_key,
            SecretString=secret_value,
            Tags=tags
        )

    def get_secret_arn(self, secret_name: str):
        return self.client.get_secret_value(SecretId=secret_name)["SecretString"]
