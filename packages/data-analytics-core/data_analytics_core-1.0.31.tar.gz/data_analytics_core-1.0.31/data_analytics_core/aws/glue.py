"""
AWS_Glue
Class containing all the needed AWS Glue service elements, actions and the client itself.
"""
from botocore.exceptions import ClientError
# custom imports
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface


class AmazonWebServicesGlue(AmazonWebServicesInterface):
    def __init__(self, region_name="eu-central-1"):
        super().__init__(region_name=region_name, service_name="glue")

    def run_job(self, job_name, job_arguments):
        self.client.start_job_run(JobName=job_name, Arguments=job_arguments)

    def get_job_status(self, job_name) -> str:
        try:
            job_run_id = self.client.get_job_runs(JobName=job_name, MaxResults=1).get("JobRuns")[0].get("Id")
            status_detail = self.client.get_job_run(JobName=job_name, RunId=job_run_id, PredecessorsIncluded=False)
            status = status_detail.get("JobRun").get("JobRunState")
            return status
        except ClientError as e:
            raise ClientError("boto3 client error in run_glue_job_get_status: " + e.__str__(),
                              operation_name="get_job_runs")
        except IndexError:
            return 'STOPPED'
        except Exception as e:
            raise Exception("Unexpected error in run_glue_job_get_status: " + e.__str__())
