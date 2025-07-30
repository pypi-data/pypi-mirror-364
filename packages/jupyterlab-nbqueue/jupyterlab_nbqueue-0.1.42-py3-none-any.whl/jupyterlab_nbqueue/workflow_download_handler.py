import logging
import importlib.resources as pkg_resources
import tornado
import tornado.web
import sys
import boto3
import os

from logging import Logger
from shutil import which

from jupyter_server.base.handlers import APIHandler

from .common.requests_utils import (
    get_request_attr_value,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class WorkflowDownloadHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        logger.info("Getting workflow logs")
        try:
            workflow_name = get_request_attr_value(self, "workflow_name")
            logger.info(f"workflow_name => {type(workflow_name)} {workflow_name}")
            bucket = get_request_attr_value(self, "bucket")
            logger.info(f"bucket => {type(bucket)} {bucket}")

            if not workflow_name:
                raise Exception("The request to the extension backend is not valid")
            if not bucket:
                raise Exception("The request to the extension backend is not valid")

            s3_client = boto3.client('s3')
            response = s3_client.download_file(
                bucket, workflow_name, os.path.basename(workflow_name)
            )
        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.status_code = 204
            self.finish(None)
