"""The workflow registry class exposes utilities to manage Workflows in the workflow table."""
import io
import pathlib

import redis
import boto3
import json
import uuid

from salt import settings
from salt.backend.workflow_service import workflow_pb2

from google.protobuf.json_format import MessageToDict

from loguru import logger


MIN_PART_SIZE = 5 * 1024 * 1024  # 5MB


class WorkflowRegistry:
    def __init__(self):
        self._redis = redis.Redis(
            host=settings.redis_settings.redis_url,
            port=settings.redis_settings.redis_port,
            db=settings.redis_settings.redis_workflow_db,
        )
        self._s3 = boto3.client(
            "s3",
            endpoint_url=settings.s3_settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_settings.s3_aws_access_key_id,
            aws_secret_access_key=settings.s3_settings.s3_aws_secret_access_key
        )

    def register_workflow(self, request_iterator):
        """This method registers a user uploaded workflow in the backend registry."""
        first_chunk: workflow_pb2.Workflow = next(request_iterator)
        version = first_chunk.version or "unknown"
        s3_key = f"{first_chunk.workflow_id}/{version}/workflow.pex"
        redis_key = f"{first_chunk.owner}:{version}:{first_chunk.workflow_id}"

        # Wrap iterator so we can prepend the first message
        def prepend_first():
            yield first_chunk
            yield from request_iterator

        wf_meta = MessageToDict(first_chunk, preserving_proto_field_name=True)
        wf_meta.pop("chunk")
        uid = str(uuid.uuid4())
        wf_meta["id"] = uid

        self._redis.set(redis_key, json.dumps(wf_meta))

        # We do keep a light weighted version of metadata for s3.
        wf_meta.pop("triggers")
        wf_meta.pop("schedule")
        logger.info("Workflow registered in the backend.")

        self.s3_multipart_upload(s3_key, prepend_first(), wf_meta)

    def s3_multipart_upload(self, key, request_iterator, wf_meta):
        upload_id = self._s3.create_multipart_upload(Bucket="workflows", Key=key, Metadata=wf_meta)[
            "UploadId"
        ]
        parts = []
        part_number = 1
        buffer = io.BytesIO()

        try:
            for request in request_iterator:
                buffer.write(request.chunk)

                if buffer.tell() >= MIN_PART_SIZE:
                    buffer.seek(0)
                    response = self._s3.upload_part(
                        Bucket="workflows",
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=buffer
                    )
                    parts.append({"PartNumber": part_number, "ETag": response["ETag"]})
                    part_number += 1
                    buffer = io.BytesIO()

            # Final chunk
            if buffer.tell() > 0:
                buffer.seek(0)
                response = self._s3.upload_part(
                    Bucket="workflows",
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=buffer
                )
                parts.append({"PartNumber": part_number, "ETag": response["ETag"]})

            # Complete upload
            self._s3.complete_multipart_upload(
                Bucket="workflows",
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts}
            )
            logger.info("Workflow registered successfully.")

        except Exception as e:
            logger.info("Could not register workflow: ", e)
            self._s3.abort_multipart_upload(
                Bucket="workflows", Key=key, UploadId=upload_id
            )
            raise

    def s3_download_workflow_binary(self, workflow_file_path: pathlib.Path, workflow: workflow_pb2.Workflow):
        s3_key = f"{workflow.workflow_id}/{workflow.version}/workflow.pex"

        self._s3.download_file("workflows", s3_key, workflow_file_path)
