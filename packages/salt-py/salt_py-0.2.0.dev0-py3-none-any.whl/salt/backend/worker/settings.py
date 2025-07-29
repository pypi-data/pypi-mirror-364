from typing import Optional

from pydantic_settings import BaseSettings

class WorkflowWorkerSettings(BaseSettings):
    queue: Optional[str] = "workflows"


workflow_worker_settings = WorkflowWorkerSettings()
