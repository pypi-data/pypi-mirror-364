"""
AWS_RDS
Class containing all the needed AWS RDS connections, actions and the client itself.
"""
from typing import Optional
import sqlalchemy
# custom imports
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface
from data_analytics_core.aws.secrets_manger import AmazonWebServicesSecretsManager
from data_analytics_core.exceptions.infrastructure.aws_infrastructure_exceptions import ErrorRDSClusterNotFound
from data_analytics_core.logger import da_logger


class AmazonWebServicesRDS(AmazonWebServicesInterface):
    def __init__(self, region_name="eu-central-1"):
        super().__init__(region_name=region_name, service_name="rds")
        self.rds_instance = None
        self.rds_cluster = None
        self.rds_endpoint = None
        self.sa_engine = None

    def create_cluster_connection(self, cluster_arn_or_name: str, secret_arn_or_name: Optional[str],
                                  schema: str, username: Optional[str], password: Optional[str]):
        if self.rds_endpoint or self.sa_engine:
            da_logger.warning(f'Found an already established connection in endpoint or engine values.'
                              f'{da_logger.new_line()}'
                              f'Endpoint: {self.rds_endpoint}'
                              f'{da_logger.new_line()}'
                              f'Engine: {self.sa_engine}')
            self.close_connection()
        try:
            self.rds_cluster = self.client.describe_db_clusters(DBClusterIdentifier=cluster_arn_or_name)
            self.rds_endpoint = self.rds_cluster['DBClusters'][0]['Endpoint']
        except Exception:
            raise ErrorRDSClusterNotFound(f'The given cluster arn was not found: {cluster_arn_or_name} .'
                                          f'{da_logger.new_line()}'
                                          f'This can also be caused by the cluster not having '
                                          f'any connection endpoint enabled.')
        self._create_engine(password, schema, secret_arn_or_name, username)

    def create_instance_connection(self, instance_arn_or_name: str, secret_arn_or_name: Optional[str],
                                   schema: str, username: Optional[str], password: Optional[str]):

        if self.rds_endpoint or self.sa_engine:
            da_logger.warning(f'Found an already established connection in endpoint or engine values.'
                              f'{da_logger.new_line()}'
                              f'Endpoint: {self.rds_endpoint}'
                              f'{da_logger.new_line()}'
                              f'Engine: {self.sa_engine}')
            self.close_connection()
        try:
            self.rds_instance = self.client.describe_db_instances(DBInstanceIdentifier=instance_arn_or_name)
            self.rds_endpoint = self.rds_instance['DBClusters'][0]['Endpoint']
        except Exception:
            raise ErrorRDSClusterNotFound(f'The given cluster arn was not found: {instance_arn_or_name} .'
                                          f'{da_logger.new_line()}'
                                          f'This can also be caused by the cluster not having '
                                          f'any connection endpoint enabled.')
        self._create_engine(password, schema, secret_arn_or_name, username)

    def _create_engine(self, password: Optional[str], schema: str,
                       secret_arn_or_name: Optional[str], username: Optional[str]):
        if secret_arn_or_name:
            secret = AmazonWebServicesSecretsManager().extract_secret_value_as_dict(
                secret_arn_or_name=secret_arn_or_name
            )
            self.sa_engine = sqlalchemy.create_engine(
                url=f'mysql+pymysql://{secret["username"]}:{secret["password"]}@{self.rds_endpoint}/{schema}'
            )
        else:
            self.sa_engine = sqlalchemy.create_engine(
                url=f'mysql+pymysql://{username}:{password}@{self.rds_endpoint}/{schema}'
            )
        da_logger.info(f'Established connection to RDS endpoint: {self.rds_endpoint}')

    def close_connection(self):
        self.sa_engine.close()
        self.rds_endpoint = None
        self.sa_engine = None
