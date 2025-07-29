import json
import logging
import importlib.resources as pkg_resources
import tornado
import tornado.web
import shlex
import subprocess
import sys
import os
import boto3
import re

from logging import Logger
from shutil import which

from jupyter_server.base.handlers import APIHandler

from .common.requests_utils import (
    get_request_attr_value,
)

from .common.variables import (
    SOURCE,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class WorkflowHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            json_body = self.get_json_body()
            logger.info(json_body)
            if json_body is None:
                raise Exception("Request body is missing.")
            if json_body["file"] is None:
                raise Exception("Notebook's metadata is missing.")
            if json_body["file"]["name"] is None:
                raise Exception("Notebook's name is missing.")
            if json_body["file"]["path"] is None:
                raise Exception("Notebook's path is missing.")
            if json_body["cpu"] is None:
                raise Exception("Notebook's CPU parameter is missing.")
            if json_body["ram"] is None:
                raise Exception("Notebook's RAM parameter is missing.")
            if json_body["bucket"] is None:
                raise Exception("S3 Bucket ID parameter is missing.")
            if json_body["conda"] is None:
                raise Exception("Conda environment parameter is missing.")
            if json_body["container"] is None:
                raise Exception("Container image parameter is missing.")

            file = json_body["file"]["name"]
            path = json_body["file"]["path"]
            cpu = json_body["cpu"]
            ram = json_body["ram"]
            bucket = json_body["bucket"]
            conda = json_body["conda"]
            container = json_body["container"]

            full_url = self.request.full_url()
            # full_url = "http://localhost:63118/user/jovyan/jupyterlab-nbqueue/workflows"
            match = re.search("(\/user\/)(.*)(\/jupyterlab-nbqueue)", full_url)
            logger.info(match.group(2))
            user = match.group(2)

            file_name, file_extension = os.path.splitext(file)
            file_path, file_extension = os.path.splitext(path)
            client_type = "signed"
            if bucket:
                logger.info("Generating conda environment file...")
                conda_cmd_split = shlex.split(f"{which('conda')} list --explicit")
                with open(f"{file_path}.txt", "w") as f_obj:
                    process = subprocess.Popen(
                        conda_cmd_split, stdout=f_obj, stderr=subprocess.PIPE
                    )
                    if process.wait() != 0:
                        logger.info("There were some errors creating the conda file")
                    f_obj.close()

                logger.info("Uploading notebook to S3...")
                with pkg_resources.path("jupyterlab_nbqueue", "cmd_launcher.py") as p:
                    logger.info(
                        f"{which('python')} {p} {bucket} {client_type} {file_path}{file_extension} input/{user}/{file_name}/{file_name}{file_extension} {cpu} {ram} {conda} {container}"
                    )
                    cmd_split = shlex.split(
                        f"{which('python')} {p} {bucket} {client_type} {file_path}{file_extension} input/{user}/{file_name}/{file_name}{file_extension} {cpu} {ram} {conda} {container}"
                    )
                    process = subprocess.Popen(
                        cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )

                    if process:
                        out, error = process.communicate()

                        if out:
                            logger.info(out)

                        if error:
                            logger.error(error)

                logger.info("Uploading conda environment file to S3...")
                with pkg_resources.path("jupyterlab_nbqueue", "cmd_launcher.py") as p:
                    logger.info(
                        f"{which('python')} {p} {bucket} {client_type} {file_path}.txt input/{user}/{file_name}/{file_name}.txt {cpu} {ram} {conda} {container}"
                    )
                    cmd_split = shlex.split(
                        f"{which('python')} {p} {bucket} {client_type} {file_path}.txt input/{user}/{file_name}/{file_name}.txt {cpu} {ram} {conda} {container}"
                    )
                    process = subprocess.Popen(
                        cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )

        except Exception as exc:
            logger.error(exc)
        else:
            self.finish(
                json.dumps(
                    {
                        "data": {
                            "name": json_body["file"]["name"],
                            "path": json_body["file"]["path"],
                        },
                    }
                )
            )
        finally:
            if process:
                out, error = process.communicate()

                if out:
                    logger.info(out)

                if error:
                    logger.error(error)

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

            s3_client = boto3.client("s3")
            response = s3_client.get_object(Bucket=bucket, Key=workflow_name)
            object_content = response["Body"].read().decode("utf-8")
        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.status_code = 200
            self.finish(object_content if object_content else "")

    @tornado.web.authenticated
    def delete(self):
        logger.info("Deleting a workflow by name")
        try:
            workflow_name = get_request_attr_value(self, "workflow_name")
            logger.info(f"workflow_name => {type(workflow_name)} {workflow_name}")
            bucket = get_request_attr_value(self, "bucket")
            logger.info(f"bucket => {type(bucket)} {bucket}")

            if not workflow_name:
                raise Exception("The request to the extension backend is not valid")
            if not bucket:
                raise Exception("The request to the extension backend is not valid")

            s3_client = boto3.client("s3")
            response = s3_client.delete_object(Bucket=bucket, Key=workflow_name)
            print(response)

            message = None
            if "DeleteMarker" in response:
                message = "File could not be deleted"

        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.set_status(204)
            self.finish(message if message else None)
