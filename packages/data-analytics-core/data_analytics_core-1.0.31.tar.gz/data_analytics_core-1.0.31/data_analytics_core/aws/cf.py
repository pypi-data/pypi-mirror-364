"""
AWS_CF Class
containing all the needed AWS CloudFormation actions and the client itself.
"""
import os
import json
import time
import ruyaml
import re
from typing import Optional
# custom imports
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface
from data_analytics_core.data_morphing.yaml_morphers import transform_yaml_to_dict
from data_analytics_core.logger import da_logger


class AmazonWebServicesCF(AmazonWebServicesInterface):
    def __init__(self, region_name="eu-central-1"):
        super().__init__(region_name=region_name, service_name='cloudformation')

    def create_resource(self, resource_name: str, path_to_file: str,
                        role_arn: str = None, tags: list[dict] = None, file_format_yaml: bool = True):

        if file_format_yaml:
            with open(path_to_file, 'r') as yaml_file:
                yaml_content = transform_yaml_to_dict(ruyaml.round_trip_load(yaml_file))
                yaml_content = self._cloudformation_tag_converter(yaml_str=yaml_content)
                self.client.create_stack(
                    StackName=resource_name,
                    TemplateBody=yaml_content,
                    RoleARN=role_arn,
                    OnFailure="ROLLBACK",
                    Tags=tags
                )
        else:
            with open(path_to_file, 'r') as json_file:
                self.client.create_stack(
                    StackName=resource_name,
                    TemplateBody=str(json.load(json_file)),
                    RoleARN=role_arn,
                    OnFailure="ROLLBACK",
                    Tags=tags
                )
        self._validate_stack_status(resource_name=resource_name)

    # TODO: keep adding tags and functions to the converter
    @staticmethod
    def _cloudformation_tag_converter(yaml_str):
        while re.search(r"\$\{env\:(\w*)\}", string=str(yaml_str)) is not None:
            for result in re.findall(r"(\$\{env\:(\w*)\})", string=str(yaml_str)):
                yaml_str = re.sub(pattern=r"(\$\{env\:"+f"{result[1]}"+r"\})",
                                  repl=os.environ.get(result[1]), string=str(yaml_str))
        while re.search(r"\$\{opt\:\w*\}", string=str(yaml_str)) is not None:
            for result in re.findall(r"(\$\{opt\:(\w*)\})", string=str(yaml_str)):
                yaml_str = re.sub(pattern=r"(\$\{opt\:"+f"{result[1]}"+r"\})",
                                  repl=os.environ.get(result[1]), string=str(yaml_str))
        while re.search(r"\$\{self\:provider\.stackTags\.Project\}", string=str(yaml_str)) is not None:
            for result in re.findall(r"(\$\{self\:provider\.stackTags\.(Project)\})", string=str(yaml_str)):
                yaml_str = re.sub(pattern=r"(\$\{self\:provider\.stackTags\.(Project)\})",
                                  repl=os.environ.get(result[1]), string=str(yaml_str))
        while re.search(r"\!R[ef|EF]*\s[\w-]*", string=str(yaml_str)) is not None:
            for result in re.findall(r"(\!R[ef|EF]*\s([\w-]*))", string=str(yaml_str)):
                yaml_str = re.sub(pattern=r"(\![Ref|REF]*\s([\w-]*))",
                                  repl=os.environ.get(result[1]), string=str(yaml_str))
        return yaml_str

    def _validate_stack_status(self, resource_name):
        while self.check_stack_status(resource_name) in [
            'CREATE_IN_PROGRESS', 'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
            'UPDATE_ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'REVIEW_IN_PROGRESS',
            'IMPORT_IN_PROGRESS', 'IMPORT_ROLLBACK_IN_PROGRESS'
        ]:
            da_logger.info(f"Creating {resource_name}. Be patient please. :)")
            time.sleep(2)
        stack_status = self.check_stack_status(resource_name)
        if stack_status in ['CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED', 'UPDATE_ROLLBACK_FAILED']:
            da_logger.error(f"Stack {resource_name} failed to achieve its expected action! {da_logger.new_line()}"
                            f"Last known status: {stack_status}")
        elif stack_status in ['ROLLBACK_IN_PROGRESS', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE',
                              'UPDATE_ROLLBACK_COMPLETE', 'IMPORT_ROLLBACK_FAILED', 'IMPORT_ROLLBACK_COMPLETE']:
            da_logger.warning(f"Stack {resource_name} has rolled back with the last status being: {stack_status}")
        elif stack_status in ['CREATE_COMPLETE', 'DELETE_COMPLETE', 'UPDATE_COMPLETE', 'IMPORT_COMPLETE']:
            da_logger.info(f"Stack {resource_name} reached successfully the status {stack_status}")

    def check_stack_status(self, resource_name) -> Optional[str]:
        return self.client.describe_stacks(StackName=resource_name)["Stacks"][0]["StackStatus"]
