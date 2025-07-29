from grpc_tools import protoc

from pathlib import Path

from loguru import logger


def generate_code(proto_path: Path, output_dir: Path):
    proto_path = Path(proto_path).resolve()
    if not proto_path.exists():
        raise FileNotFoundError(f"Path {proto_path} does not exist.")

    proto_files = list(proto_path.rglob("*.proto"))
    if not proto_files:
        raise FileNotFoundError("No .proto files found in the specified path.")

    abs_protos = []

    for proto_file in proto_files:
        abs_protos.append(str(proto_file))

    logger.info(f"Proto path: {proto_path}")
    logger.info(f"output_dir path: {output_dir}")
    result = protoc.main(
        [
            "grpc_tools.protoc",
            f"--proto_path={proto_path}",  # proto include path
            f"--python_out={output_dir}",  # generate *_pb2.py
            f"--grpc_python_out={output_dir}",  # generate *_pb2_grpc.py
            f"--pyi_out={output_dir}",
            " ".join(abs_protos),
        ]
    )

    if result != 0:
        logger.error(f"Failed to generate code.")
    else:
        logger.info(f"✅ Success!")
