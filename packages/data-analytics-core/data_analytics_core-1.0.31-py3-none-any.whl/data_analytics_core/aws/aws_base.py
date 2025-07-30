import os
from abc import ABC
import boto3
# custom imports
from data_analytics_core.localstack.boto_client_moks.localstack_clients import boto3_client_localstack, \
    boto3_resource_localstack


class AmazonWebServicesInterface(ABC):

    def __init__(self, service_name: str, region_name: str = "eu-central-1", needs_resource_init: bool = False,
                 boto3_session: boto3.session.Session = None):
        self.region_name = region_name
        self.boto3_session = boto3_session if boto3_session is not None else boto3.session.Session()
        self._set_environment_location(service_name, needs_resource_init)

    def _set_environment_location(self, service_name: str, needs_resource_init: bool):
        if os.getenv("LOCALSTACK_ENDPOINT_URL"):
            self.client = boto3_client_localstack(service_name=service_name, region_name=self.region_name,
                                                  boto3_session=self.boto3_session)
        else:
            self.client = self.boto3_session.client(service_name, region_name=self.region_name)
        if needs_resource_init:
            if os.getenv("LOCALSTACK_ENDPOINT_URL"):
                self.resource = boto3_resource_localstack(service_name=service_name, region_name=self.region_name,
                                                          boto3_session=self.boto3_session)
            else:
                self.resource = self.boto3_session.resource(service_name, region_name=self.region_name)
