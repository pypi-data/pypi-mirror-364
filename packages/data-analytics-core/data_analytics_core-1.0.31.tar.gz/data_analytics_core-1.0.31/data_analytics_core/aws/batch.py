"""
AWS_BatchJob Class
Class containing all the needed AWS Service Manager actions and the client itself.
"""
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface
from data_analytics_core.logger.da_core_logger import da_logger


class AmazonWebServicesBatchJobs(AmazonWebServicesInterface):
    def __init__(self, region_name="eu-central-1", environment_default_parameters_dict: dict = None):
        super().__init__(region_name=region_name, service_name="batch")
        # custom variables
        self.environment_default_parameters_dict = environment_default_parameters_dict

    def run_batch_with_parameters(self):
        if self.environment_default_parameters_dict:
            response = self.client.submit_job(
                jobName=self.environment_default_parameters_dict.get("job_name"),
                jobQueue=self.environment_default_parameters_dict.get("job_queue_name"),
                jobDefinition=self.environment_default_parameters_dict.get("job_definition_name"),
                propagateTags=True,
                timeout={"attemptDurationSeconds": int(self.environment_default_parameters_dict.get("batch_job_timeout"))},
            )
            da_logger.info(message=f"Batch Job started succesfully with:{da_logger.new_line()}"
                                    f"Job name:{response.get('jobName')}{da_logger.new_line()}"
                                    f"Job ID:{response.get('jobId')}")
        else:
            # TODO: change this to a try except
            da_logger.error("We have missing parameters!")

