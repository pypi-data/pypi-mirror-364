import glob

import grpc
import typer
import yaml

from pathlib import Path

from salt.settings import workflow_service_settings
from salt.backend.workflow_service.workflow_pb2 import Workflow
from salt.backend.workflow_service.workflow_pb2_grpc import WorkflowServiceStub

from google.protobuf.json_format import ParseDict
from loguru import logger


def register_workflow(project_path: Path):
    """Given a path to a python or C# project, will take care of uploading its artifact to the backend workflow service."""
    salt_file = project_path / "salt.yaml"
    if not salt_file.exists():
        logger.error(f"No salt.yaml found at {salt_file}")
        raise typer.Exit(code=1)

    def request_generator(workflow: Workflow, file_path: Path):
        with open(file_path, "rb") as f:
            chunk_size = 1024 * 1024  # 1MB
            while chunk := f.read(chunk_size):
                workflow.MergeFrom(
                    Workflow(
                        chunk=chunk,
                    )
                )
                yield workflow

    # Ensure the build folder exists and contains either a valid executable or pex file.

    # TODO support remote server
    # TODO support different kind of projects
    logger.info(f"Making sure the build folder exists...")
    pex = glob.glob(f"{str(project_path)}/**/*.pex", recursive=True)
    if not pex:
        raise Exception(
            "No build artifacts found! Make sure you build your project first using `salt build <path>`."
        )

    with open(salt_file, "r") as f:
        salt_data = yaml.safe_load(f)
    wf = ParseDict(salt_data, Workflow())

    with grpc.insecure_channel(f"{workflow_service_settings.workflow_service_url}:{workflow_service_settings.workflow_service_port}") as channel:
        response = WorkflowServiceStub(channel=channel).RegisterWorkflow(
            request_generator(wf, pex.pop())
        )
        logger.info(response.message)


def get_workflow_binary():
    """Given workflow metadata, downloads the binary from S3."""
    pass

if __name__ == "__main__":
    import pathlib

    register_workflow(pathlib.Path("../../../../examples/python-dag").absolute())
