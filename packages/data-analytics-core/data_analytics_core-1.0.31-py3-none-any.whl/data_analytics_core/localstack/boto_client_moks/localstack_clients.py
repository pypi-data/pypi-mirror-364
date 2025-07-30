import os
import boto3


def boto3_client_localstack(service_name: str, region_name: str = "eu-central-1",
                            boto3_session: boto3.session.Session = boto3.session.Session()) -> boto3.session.Session.client:
    """
    boto3 client for setup environment
    """
    return boto3_session.client(
        service_name=service_name,
        endpoint_url=os.getenv("LOCALSTACK_ENDPOINT_URL"),
        use_ssl=False,
        verify=False,
        aws_access_key_id="localstack",
        aws_secret_access_key="test",
        region_name=region_name,
    )


def boto3_resource_localstack(service_name: str, region_name: str = "eu-central-1",
                              boto3_session: boto3.session.Session = boto3.session.Session()) -> boto3.session.Session.resource:
    return boto3_session.resource(
        service_name=service_name,
        endpoint_url=os.getenv("LOCALSTACK_ENDPOINT_URL"),
        use_ssl=False,
        verify=False,
        aws_access_key_id="localstack",
        aws_secret_access_key="test",
        region_name=region_name,
    )
