"""
AWS_SSM
Class containing all the needed AWS Service Manager actions and the client itself.
"""
from typing import Optional
import json
# custom imports
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface


class AmazonWebServicesSSM(AmazonWebServicesInterface):
    def __init__(self, region_name="eu-central-1"):
        super().__init__(region_name=region_name, service_name="ssm")

    def extract_param_value_as_dict(self, param_name: str) -> Optional[dict]:
        return eval(json.loads(json.dumps(self.client.get_parameter(Name=param_name)["Parameter"]["Value"])))

    def extract_param_value_as_string(self, param_name: str) -> Optional[str]:
        return self.client.get_parameter(Name=param_name)["Parameter"]["Value"]
