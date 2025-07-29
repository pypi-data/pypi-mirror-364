import glob
import pathlib
import sys
import subprocess

import build
import typer
import docker

from pex.bin.pex import main as pex_main
from loguru import logger


def build_pex(pyproject_path: pathlib.Path):
    """Given the path to a python project, builds it into a .pex file using pex."""
    pyproject_file = pyproject_path / "pyproject.toml"

    if not pyproject_file.exists():
        logger.error(f"Error: No pyproject.toml found at {pyproject_file}")
        raise typer.Exit(code=1)

    build_output = (pyproject_path / "build").resolve()
    pyproject_path = pyproject_path.resolve()
    dist_location = pyproject_path / "dist"

    logger.info(f"Building project: {pyproject_path} to: {build_output}")

    #builder = build.ProjectBuilder(pyproject_path)
    #builder.build("wheel", output_directory=dist_location)

    #logger.info(f"Building {pyproject_path} project into executable...")
    #wheel = glob.glob(f"{str(dist_location)}/**/*.whl", recursive=True).pop()

    # Build happens in a docker container to ensure platform compatibility.

    client = docker.from_env()

    container_project_dir = "/app"

    command = (
        f"python -m build {container_project_dir}"
    )
    container = client.containers.run(
        image="salt:latest",
        command=["sh", "-c", command],
        volumes={
            str(pyproject_path): {"bind": container_project_dir, "mode": "rw"}
        },
        detach=True,
        stdout=True,
        stderr=True
    )
    logs = container.logs().decode()

    exit_code = container.wait()["StatusCode"]
    logger.info(logs)
    wheel = glob.glob(f"{str(dist_location)}/**/*.whl", recursive=True).pop()

    sys.argv = [
        "pex",
        f"{wheel}",
        "-o",
        f"{build_output}/main.pex",
        "-m",
        f"{pyproject_path.name}.main:main",
    ]

    pex_main()


if __name__ == '__main__':
    python_dag = pathlib.Path(__file__).parent.parent.parent.parent / "examples" / "python-dag"

    build_pex(python_dag)

