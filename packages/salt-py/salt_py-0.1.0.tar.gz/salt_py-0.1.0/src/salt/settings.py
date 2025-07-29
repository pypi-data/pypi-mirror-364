from typing import Optional

from pydantic_settings import BaseSettings


class Redis(BaseSettings):
    redis_url: Optional[str] = "localhost"
    redis_port: Optional[int] = "6379"
    redis_workflow_db: Optional[int] = 0


class RabbitSettings(BaseSettings):
    rabbit_url : Optional[str] = "localhost"
    rabbit_port : Optional[int] = "5672"
    rabbit_user : Optional[str] = "admin"
    rabbit_password: Optional[str] = "admin"


class S3Settings(BaseSettings):
    s3_endpoint_url: Optional[str] = "http://localhost:9000"
    s3_aws_access_key_id: Optional[str] = "miniadmin"
    s3_aws_secret_access_key: Optional[str] = "miniadmin"


class WorkflowServiceSettings(BaseSettings):
    workflow_service_url: Optional[str] = "localhost"
    workflow_service_port: Optional[str] = "50051"


redis_settings = Redis()
rabbit_settings = RabbitSettings()
s3_settings = S3Settings()
workflow_service_settings = WorkflowServiceSettings()
