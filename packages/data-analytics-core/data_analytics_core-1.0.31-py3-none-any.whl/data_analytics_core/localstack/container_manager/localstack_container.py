"""
Local Stack container manager Class
"""
import os
from typing import Optional
import docker.client
import dotenv
import requests
from docker.errors import APIError
from dotenv import dotenv_values
from testcontainers.localstack import LocalStackContainer
# custom imports
from data_analytics_core.logger.da_core_logger import da_logger
from data_analytics_core.localstack.set_up.infrastructure import LocalstackCommonInfrastructure


class LocalStackContainerManager:
    """
    This class is used to initialize the LocalStack dockerized environment.
    To make sure this happens as expected, it is recommended to have the docker desktop already activated,
    and with the images downloaded.
    Also keep in mind that everytime this class is initialized,
    it will attempt to kill any LS previous instance with a proper name,
    yet it will not terminate the instance if the method "stop" is not called.
    """
    local_stack_container = None
    os.environ["LOCALSTACK_ENDPOINT_URL"] = ''

    def __init__(self,
                 project_name: str,
                 list_of_environment_variables: Optional[list[dict]],
                 path_to_env_file: str = None,
                 ls_docker_container_name: str = "AWSLocalStackMock",
                 got_pro_licence_and_auth: bool = False,
                 image_version: str = "0.14.2",
                 pro_image_version: str = "3.2.0"):
        self.image_version = image_version
        self.pro_image_version = pro_image_version
        self._docker_image_generator(got_pro_licence_and_auth, ls_docker_container_name)
        self.project_name = project_name
        if path_to_env_file:
            self.local_stack_container.env.update(dict(dotenv_values(path_to_env_file)))
            # This will make sure any env you are on gets the same vars
            dotenv.load_dotenv(path_to_env_file)
        self._start()
        self.s3_port = "4566"
        self._generate_internal_env_vars()
        self.generate_env_vars_from_dict_list(list_of_environment_variables)
        self.common_infra = LocalstackCommonInfrastructure(s3_port=self.s3_port)
        da_logger.info("Common infra emulated")

    def _docker_image_generator(self, got_pro_licence_and_auth, ls_docker_container_name):
        if not got_pro_licence_and_auth:
            image_repository = f"localstack/localstack:{self.image_version}"

        else:
            image_repository = f"localstack/localstack-pro:{self.pro_image_version}"
        docker.client.APIClient().pull(repository=image_repository)
        self.local_stack_container = (
            LocalStackContainer(image_repository).with_env("DATA_DIR", "/tmp/localstack/data").
            with_exposed_ports(4566).with_name(ls_docker_container_name)
        )

    def _start(self):
        try:
            self.local_stack_container.start().with_kwargs()
            da_logger.info("No previous docker was mounted")
        except (AttributeError, APIError, requests.exceptions.HTTPError):
            # TODO: evaluate below bash to check on alternatives to kill doc command
            os.system("docker rm -f $(docker container ls -q --filter name='AWS*')")
            da_logger.info("Previous docker was mounted and running. It has been successfully terminated")
            self.local_stack_container.start()
        da_logger.info("Localstack container started")

    def stop(self):
        """
        https://docs.python.org/3/library/unittest.html#unittest.TestResult.stopTestRun
        Called once after all tests are executed.
        :return:
        """
        self.local_stack_container.stop()
        da_logger.info("Localstack container stopped")

    def _generate_internal_env_vars(self) -> None:
        os.environ["LOCALSTACK_ENDPOINT_URL"] = f"http://localhost:{self.s3_port}"
        os.environ["env"] = "localstack"
        os.environ["project"] = self.project_name

    @staticmethod
    def generate_env_vars_from_dict_list(list_of_dicts: Optional[list[dict]]):
        if list_of_dicts:
            for dictionary in list_of_dicts:
                for key, value in dictionary.items():
                    os.environ[key] = value
