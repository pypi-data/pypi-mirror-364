"""
AWS_S3 Class containing all the needed AWS Service Manager actions and the client itself.
"""
import io
from typing import Optional
import urllib.parse
import re
import boto3
import botocore.exceptions
import botocore.client
import pandas as pd
from pandas.errors import EmptyDataError
import awswrangler
# custom imports
from data_analytics_core.aws.aws_base import AmazonWebServicesInterface
from data_analytics_core.exceptions.infrastructure.aws_infrastructure_exceptions import (
    FileDialectEncodingNotExpectedError, ProviderPrefixError)
from data_analytics_core.logger.da_core_logger import da_logger


# TODO: add local env discrimination logic is_aws = True if os.environ.get("AWS_DEFAULT_REGION") else False
# TODO: add upload object (generic, not csv)
class AmazonWebServicesS3(AmazonWebServicesInterface):
    """
    AWS S3 service management class. Works for both, localstack and AWS environments.
    The expected partitions for events (bucket & prefixes) are the following:
    "bucket"/"data_provider"/year=yyyy/month=mm/filename.IDK
    The parameter "get_provider_prefix" can be used by any means for another kind of initial partition,
    even if the year partition is not expected afterward.
    The class can be instantiated directly over an event and working on the file/data related to this event,
    but can also work as a standalone class.
    """
    def __init__(self, eventbridge_event=None, bucket=None,
                 region_name="eu-central-1", get_provider_prefix: bool = False,
                 key: str = None, boto3_session: boto3.session.Session = None):
        super().__init__(region_name=region_name, service_name="s3", needs_resource_init=True,
                         boto3_session=boto3_session)
        # custom variables
        self.bucket = bucket
        self.eventbridge_event = eventbridge_event
        if key is not None:
            self.key = key
        if self.eventbridge_event:
            # from eventbridge s3 eventbridge_event
            self.key = urllib.parse.unquote_plus(self.eventbridge_event['detail']['object']['key'], encoding='utf-8')
            self.bucket = self.eventbridge_event['detail']['bucket']['name']
        if get_provider_prefix:
            if re.match(pattern=r"year", string=self.key):
                self.provider_prefix = re.match(pattern=r"^(.(?!year))*",
                                                string=self.key).group(0)
            else:
                self.provider_prefix = re.match(pattern=r"(\w+)",
                                                string=self.key).group(0)
            if not self.provider_prefix:
                raise ProviderPrefixError(f'Error in file with key: {self.key}{da_logger.new_line()}'
                                          f'It is not a provider from the expected ones,'
                                          f'or this file is not inside the prefix it should')

    def get_file_content_from_excel(self, **pandas_kwargs) -> pd.DataFrame:
        """
        This function downloads a file from bucket. The expected file should be an excel file.
        The pandas kwargs can be the following:
            https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        returns a dataframe
        """
        return awswrangler.s3.read_excel(
            path=f's3://{self.bucket}/{self.key}',
            boto3_session=self.boto3_session,
            **pandas_kwargs
        )


    def upload_dataframe_to_csv(self, dataframe: pd.DataFrame, key=None, bucket=None, is_csv=True):
        if not bucket:
            bucket = self.bucket
        if is_csv is True:
            dataframe = dataframe.to_csv(encoding="UTF-8", sep=";", decimal=".", index=False)
            self.client.upload_fileobj(io.BytesIO(bytes(dataframe, "UTF-8")), bucket, key)

    # TODO: refactor to reduce complexity but keep iteration
    def get_file_content_from_csv(self,
                                  encoding: str = None,
                                  file_body=None,
                                  separator: str = None,
                                  decimal: str = None
                                  ) -> pd.DataFrame:
        # Download file from bucket
        if not file_body:
            file_body = self.get_s3_object(self.bucket, self.key)
        # Parse file
        if not encoding:
            encoding_list = ["utf-8", "latin-1", "mac-latin2", "ISO-8859-1"]
        else:
            encoding_list = [encoding]
        if not separator:
            separator_list = [";", ",", "."]
        else:
            separator_list = [separator]
        if not decimal:
            decimal_list = [".", ","]
        else:
            decimal_list = [decimal]
        warnings_list = []
        for encoder in encoding_list:
            for separator in separator_list:
                for decimal in decimal_list:
                    try:
                        return pd.read_csv(
                            io.BytesIO(file_body.read()),
                            sep=separator,
                            encoding=encoding,
                            decimal=decimal
                        )
                    except (pd.errors.ParserError, UnicodeDecodeError, EmptyDataError):
                        warnings_list.append([f"Encoder: {encoder}", f"Separator: {separator}", f"Decimal: {decimal}"])
        raise FileDialectEncodingNotExpectedError(
            f"Found no encoder and separator combination to fit in file:"
            f"{self.key}"
            f"Combinations searched:{da_logger.new_line()}{warnings_list}")

    def get_file_content_from_txt(self):
        # Download file from bucket
        file_body = self.get_s3_object(self.bucket, self.key)
        # Parse file
        return io.BytesIO(file_body.read()).read().decode('utf-8')

    def move_file(self, key: str = None, bucket: str = None,
                  new_key=None, new_bucket=None, delete_origin_file=True) -> None:
        # Check moving parameters exist
        if not new_bucket and not new_key:
            raise AttributeError("Need to specify one at least, new_bucket and/or new_key.")
        # Prepare copying config
        if key and bucket:
            copy_source = {'Prefix': key, 'Bucket': bucket}
        else:
            copy_source = {'Prefix': self.key, 'Bucket': self.bucket}
        # Handling bucket and file empty move exceptions
        try:
            # This step is used because boto3 does not raise anything if the response inside the bucket is empty
            if self.client.list_objects_v2(**copy_source)["KeyCount"] == 0:
                raise da_logger.error(f"The prefix used: {copy_source.get('Prefix')} "
                                      f"was not found inside the bucket: {copy_source.get('Bucket')}")
        except (botocore.exceptions.ClientError, botocore.client.ClientError):
            da_logger.error(f"The bucket: {copy_source.get('Bucket')} was not found, does not exist or is misstated")
        # Executing possible move configs
        if new_key is None:
            new_key = key
        if new_bucket is None:
            new_bucket = bucket
        self.client.copy_object(Bucket=new_bucket, Key=new_key, CopySource=copy_source)
        da_logger.info(f"The file: {key}{da_logger.new_line()}From bucket: "
                       f"{bucket}{da_logger.new_line()}Has been copied to prefix: "
                       f"{new_key}{da_logger.new_line()}And bucket: {new_bucket}")
        # Delete old file (if specified)
        if delete_origin_file:
            self.resource.Object(**copy_source).delete()
            da_logger.info("The original file has been deleted.")

    def extract_year_from_key(self, key=None) -> int:
        year = re.search(r'/year=(\d{4})/', key or self.key)
        return int(year.group(1))

    def extract_month_from_key(self, key=None) -> str:
        month = re.search(r'/month=(\d{2})/', key or self.key)
        return str(month.group(1)).zfill(2)

    def get_s3_object(self, bucket_name: str, object_key: str):
        """
        Function expected to use with another formatter on top,
        although you can be use it as is.
        :param bucket_name: S.Ex.
        :param object_key: This parameter should include the full prefix and filename.
        :return: Gets the interior data of the file, without any encoding nor parsing (plain).
        """
        response = self.client.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body']

    def get_list_of_objects(self, bucket, prefix='', suffix='') -> Optional[list]:
        """
        Function to iterate inside a specific bucket and prefix, and filter by the suffix.
        Can be used without any of the two late parameters.
        :param bucket: S. Ex.
        :param prefix: Portion of the key filtered from the bucket name onwards.
        :param suffix: Portion of the key filtered from the file name backwards.
        :return: List of keys contained and matching the search.
        """
        keys_list = list(self._get_generator_list_matching_s3_keys(bucket, prefix, suffix))
        if len(keys_list):
            result_list = []
            for key in keys_list:
                result_list.append(key)
            return result_list
        else:
            return None

    # TODO: get yield information to optimize below function
    def _get_generator_list_matching_s3_keys(self, bucket: str, prefix='', suffix=''):
        """
        Generate the keys in an S3 bucket.

        :param bucket: Name of the S3 bucket.
        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        """
        kwargs = {'Bucket': bucket}
        # If the prefix is a single string (not a tuple of strings), we can
        # do the filtering directly in the S3 API.
        if isinstance(prefix, str):
            kwargs['Prefix'] = prefix

        while True:

            # The S3 API response is a large blob of metadata.
            # 'Contents' contains information about the listed objects.
            resp = self.client.list_objects_v2(**kwargs)
            if resp["KeyCount"] == 0:
                return None
            else:
                for obj in resp['Contents']:
                    key = obj['Key']
                    if key.startswith(prefix) and key.endswith(suffix):
                        yield key

            # The S3 API is paginated, returning up to 1000 keys at a time.
            # Pass the continuation token into the next response, until we
            # reach the final page (when this field is missing).
            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break
