import os
import subprocess
import sys
from testcontainers.core.container import DockerContainer
from testcontainers.mysql import MySqlContainer
# custom imports
from data_analytics_core.aws.cf import AmazonWebServicesCF
from data_analytics_core.aws.glue import AmazonWebServicesGlue
from data_analytics_core.aws.batch import AmazonWebServicesBatchJobs
from data_analytics_core.aws.s3 import AmazonWebServicesS3
from data_analytics_core.aws.secrets_manger import AmazonWebServicesSecretsManager
from data_analytics_core.aws.ssm import AmazonWebServicesSSM
from data_analytics_core.logger.da_core_logger import da_logger
from data_analytics_core.localstack.set_up.config import TESTS_FIXTURES_RAW_PATH, OUTPUTS_PATH


class LocalstackCommonInfrastructure:
    def __init__(self, s3_port, generic_boto_clients_activation: bool = True):
        self._boto_clients_activation(generic_boto_clients_activation)
        self.s3_port = s3_port
        da_logger.info(f"{sys.path}{da_logger.new_line()}{sys.path[1]}")

    def fixture_upload(self, fixture_list: list = None, fixture_bucket_name: str = None):
        if not fixture_list:
            fixture_list = self._recursive_provider_iterator(directory=TESTS_FIXTURES_RAW_PATH)
        for fixture in fixture_list:
            fixture_path = f"{TESTS_FIXTURES_RAW_PATH}/{fixture}"
            self.aws_s3.s3_client.upload_file(
                fixture_path,
                fixture_bucket_name,
                fixture,
            )
            # TODO: refactor iterating sub-levels of fixtures
            # try:
            # except IsADirectoryError:
            #     fixture_flattened_path_list = self._recursive_provider_iterator(directory=fixture_path)
            #     for flattened_fixture in fixture_flattened_path_list:
            #         flattened_fixture_path = fixture_path + flattened_fixture
            #         self.aws_s3.s3_client.upload_file(
            #             flattened_fixture_path,
            #             self.raw_bucket,
            #             fixture,
            #         )

    def create_ddbb(self, engine_type: str, engine_version: str = "latest",
                    user_name: str = "user", password: str = "supersecretpassword",
                    database_or_dataset_from_schema: str = None):
        """
        Method used to enable DDBB containers in local.
        :param engine_type: Kind of DDBB to emulate. For now the types accepted are: MySQL.
        :param engine_version:
        :param user_name:
        :param password:
        :param database_or_dataset_from_schema:
        :return:
        """
        DB_CONTAINER: DockerContainer
        DB_URL: str = ""

        db_container = None
        da_logger.info(f"Starting DDBB module of type {engine_type}")
        if engine_type == "MySQL":
            db_container = MySqlContainer(
                image=f"mysql:{engine_version}",
                MYSQL_USER=f"{user_name}",
                MYSQL_PASSWORD=f"{password}",
                MYSQL_DATABASE=f"{database_or_dataset_from_schema}",
                MYSQL_ROOT_PASSWORD="root"
            ).with_command(
                command="mysqld --default-authentication-plugin=mysql_native_password"
            )
        db_container.start()
        da_logger.info("DB container started")

        return db_container

    def cloudformation_create_stack(self, resource_name: str, path_to_file: str,
                                    role_arn: str = None, tags: list[dict] = None):
        self.aws_cf.create_resource(
            resource_name=resource_name,
            path_to_file=path_to_file,
            role_arn=role_arn,
            tags=tags
        )

    def create_s3_buckets(self, s3_bucket_list: list[str]):
        for s3_name in s3_bucket_list:
            self.aws_s3.s3_client.create_bucket(
                Bucket=s3_name,
                CreateBucketConfiguration={'LocationConstraint': self.aws_s3.region_name}
            )
            da_logger.info(f"Created new bucket called: {s3_name}")

    def get_s3_file_as_output(self,
                              aws_s3: AmazonWebServicesS3,
                              bucket=None,
                              prefix: str = '',
                              suffix: str = ''):
        """
        Function to extract data from buckets.
        If there are specified filter_buckets,only those in the list will be copied (or tuple, or set)
        """
        try:
            files_list = aws_s3.get_list_of_objects(bucket=bucket, prefix=prefix, suffix=suffix)
            for file in files_list:
                da_logger.info(f"Downloading file:{file}{da_logger.new_line()}"
                               f"From bucket {bucket}")
                command = (f"awslocal s3 cp s3://{bucket}/{file} "
                           f"{OUTPUTS_PATH}/{bucket}/ --endpoint http://localhost:"
                           f"{self.s3_port}"
                           )
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                p.communicate()
        except Exception as e:
            da_logger.error(f"Exception in {__name__} e: {e}")

    def _recursive_provider_iterator(self, directory: str) -> list:
        """
        This function expects a directory with some fixtures from data providers to be distributed into
        a bucket, to begin the data & data flow testing.
        :param directory: Path to the fixtures
        :return: list
        """
        providers = os.listdir(directory)
        files_list = []
        for provider in providers:
            files = os.listdir(f"{directory}/{provider}")
            files_list.append([(provider + "/" + unflattened) for unflattened in files])
        files_list = self._list_flatten(files_list)
        return files_list

    def _list_flatten(self, nested_lists: list) -> list:
        flat_list = []
        self._flattener(flat_list, nested_lists)
        return flat_list

    def _flattener(self, flat_list, nested_lists):
        for subelement in nested_lists:
            if isinstance(subelement, list):
                self._flattener(flat_list, subelement)
            else:
                flat_list.append(subelement)

    def _boto_clients_activation(self, generic_boto_clients_activation: bool = True):
        if generic_boto_clients_activation:
            self.aws_s3 = AmazonWebServicesS3()
            self.aws_glue = AmazonWebServicesGlue()
            self.aws_secrets_manager = AmazonWebServicesSecretsManager()
            self.aws_ssm = AmazonWebServicesSSM()
            self.aws_batch = AmazonWebServicesBatchJobs()
            self.aws_cf = AmazonWebServicesCF()
