import grpc

from concurrent.futures import ThreadPoolExecutor

from salt.backend.workflow_service import (
    workflow_pb2,
    workflow_pb2_grpc,
    workflow_registry,
)

from loguru import logger


class WorkflowService(workflow_pb2_grpc.WorkflowServiceServicer):
    def __init__(self):
        self._workflow_registry = workflow_registry.WorkflowRegistry()
        super().__init__()

    def RegisterWorkflow(self, request_iterator, context):
        """This endpoint is reached by users when running `salt register-workflow` command.

        After storing the Workflow artifact uploaded by the user, the Workflow is stored in the Graph Table in Redis.

        """
        logger.info("Received Register Workflow request.")

        self._workflow_registry.register_workflow(request_iterator)

        logger.info("Workflow File Stored.")

        return workflow_pb2.Result(success=True, message="Upload complete")


def serve():
    port = "50051"
    logger.info(f"Starting Workflow gRPC Server on port {port}...")
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    workflow_pb2_grpc.add_WorkflowServiceServicer_to_server(WorkflowService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
