import json
import logging
import sys
import re
from logging import Logger

import boto3
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

from .common.requests_utils import (
    get_request_attr_value,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class WorkflowsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        logger.info("Getting all workflows from endpoint")
        try:
            bucket = get_request_attr_value(self, "bucket")
            logger.info(f"bucket => {type(bucket)} {bucket}")

            if not bucket:
                raise Exception("The request to the extension backend is not valid")

            full_url = self.request.full_url()
            # full_url = 'http://localhost:63118/user/jovyan/jupyterlab-nbqueue/workflows'
            match = re.search("(\/user\/)(.*)(\/jupyterlab-nbqueue)", full_url)
            logger.info(match.group(2))
            user = match.group(2)

            s3_client = boto3.client("s3")
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=f"output/{user}")
            if "Contents" in response:
                workflows_raw = response["Contents"]
            else:
                print("Folder is empty.")

            workflows = (
                list(
                    map(
                        lambda workflow: {
                            "name": workflow["Key"],
                            "status": "Succeeded",
                        },
                        (
                            filter(
                                lambda workflow: workflow["Key"].endswith(".log")
                                or workflow["Key"].endswith(".ipynb"),
                                workflows_raw,
                            )
                        ),
                    )
                )
                if workflows_raw
                else []
            )

        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.status_code = 200
            self.finish(json.dumps(workflows) if workflows else [])
