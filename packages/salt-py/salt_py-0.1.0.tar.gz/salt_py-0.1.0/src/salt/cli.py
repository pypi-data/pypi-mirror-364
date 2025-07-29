import typer

from pathlib import Path

from salt.builders import py_builder

app = typer.Typer()


@app.command()
def build(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to the Python project directory (containing pyproject.toml)",
    )
):
    py_builder.build_pex(path)


@app.command()
def generate_server_code(
    proto_path: Path = typer.Argument(
        ..., exists=True, file_okay=False, dir_okay=True, readable=True
    ),
    output_dir: Path = typer.Argument(
        ..., exists=False, file_okay=False, dir_okay=True, readable=True
    ),
):
    """Generates gRPC code."""
    from salt.utils.grpc import codegen

    codegen.generate_code(proto_path, output_dir)


@app.command()
def workflow_service():
    """Starts the workflow service."""
    from salt.backend.workflow_service import workflow_service

    workflow_service.serve()


@app.command()
def register_workflow(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        help="Path to the project directory (e.g. containing pyproject.toml)",
    )
):
    """Given a path to a Project (.csproj or pyproject.toml), it builds and registers it to the Workflow Server."""
    from salt.backend.workflow_service import utils

    utils.register_workflow(path)


@app.command()
def scheduler():
    from salt.backend.scheduler import scheduler

    scheduler.Scheduler().loop()


@app.command()
def workflow_worker():
    from salt.backend.worker import workflow_worker

    workflow_worker.WorkflowWorker().loop()


if __name__ == "__main__":
    import pathlib

    # register_workflow(pathlib.Path(r"/Users/Iacopo/Documents/PyCharm/Salt/Salt/examples/python-dag"))
    scheduler()
