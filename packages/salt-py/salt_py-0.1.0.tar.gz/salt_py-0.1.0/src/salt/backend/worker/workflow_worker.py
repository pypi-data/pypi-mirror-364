"""The worker component takes care of consuming jobs from rabbitmq queues.

A worker can be initialized to a specific queue, to consume one or more types of Workflows.

Once a Workflow Schedule is consumed by the Worker, the Workflow is executed on it and the atomic tasks will
execute as defined."""
import json
import pathlib
import subprocess
import tempfile
import os

import pika

from salt import settings
from salt.backend.worker.settings import workflow_worker_settings
from salt.backend.workflow_service import workflow_registry, workflow_pb2

from google.protobuf.json_format import ParseDict
from loguru import logger


class WorkflowWorker:
    def __init__(self):
        self._rabbit = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.rabbit_settings.rabbit_url,
            credentials=pika.PlainCredentials(settings.rabbit_settings.rabbit_user,
                                              settings.rabbit_settings.rabbit_password)
        ))

        self._workflow_registry = workflow_registry.WorkflowRegistry()

    def execute_workflow(self, ch, method, properties, body):
        try:
            workflow_obj = workflow_pb2.Workflow()
            ParseDict(json.loads(body.decode()), workflow_obj, ignore_unknown_fields=True)

            # Download and execute workflow
            with tempfile.TemporaryDirectory() as tmp_dir:
                workflow_file_path = pathlib.Path(tmp_dir) / "workflow.pex"
                self._workflow_registry.s3_download_workflow_binary(workflow=workflow_obj, workflow_file_path=workflow_file_path)
                if not os.path.exists(workflow_file_path):
                    logger.error(f"Workflow file was not downloaded correctly at: {workflow_file_path}")

                logger.debug(f"Downloaded workflow binary from S3: {workflow_obj.workflow_id}")

                # Execute Workflow
                result = subprocess.run(
                    ["python3.10", str(workflow_file_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                logger.debug(result.stdout)
                logger.debug(result)

            ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge successful processing
        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def loop(self):
        channel = self._rabbit.channel()

        queue_name = workflow_worker_settings.queue
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_qos(prefetch_count=1)  # Ensure fair dispatch
        channel.basic_consume(queue=queue_name, on_message_callback=self.execute_workflow)

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

if __name__ == '__main__':
    WorkflowWorker().loop()
