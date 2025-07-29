import json

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

from jupyterlab_nbqueue.workflow_handler import WorkflowHandler
from jupyterlab_nbqueue.workflow_download_handler import WorkflowDownloadHandler
from jupyterlab_nbqueue.workflows_handler import WorkflowsHandler
from jupyterlab_nbqueue.kernels_handler import KernelsHandler
from jupyterlab_nbqueue.conda_handler import CondaHandler
from jupyterlab_nbqueue.mpi_job_handler import MpiJobHandler
from jupyterlab_nbqueue.accessible_directories_handler import AccessibleDirectoriesHandler

import tornado


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(
            json.dumps({"data": "This is /jupyterlab-nbqueue/get-example endpoint!"})
        )


def setup_handlers(web_app):
    host_pattern = ".*$"
    app_name = "jupyterlab-nbqueue"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, app_name, "get-example")
    nbqueue_workflow = url_path_join(base_url, app_name, "workflow")
    workflow_download_handler = url_path_join(base_url, app_name, "workflow/download")
    nbqueue_workflows = url_path_join(base_url, app_name, "workflows")
    nbqueue_kernels = url_path_join(base_url, app_name, "kernels")
    nbqueue_conda = url_path_join(base_url, app_name, "conda")
    submit_mpi_job = url_path_join(base_url, app_name, "submit")
    accessible_directories = url_path_join(base_url, app_name, "accessible-directories")
    handlers = [
        (route_pattern, RouteHandler),
        (nbqueue_workflow, WorkflowHandler),
        (workflow_download_handler, WorkflowDownloadHandler),
        (nbqueue_workflows, WorkflowsHandler),
        (nbqueue_kernels, KernelsHandler),
        (nbqueue_conda, CondaHandler),
        (submit_mpi_job, MpiJobHandler),
        (accessible_directories, AccessibleDirectoriesHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
