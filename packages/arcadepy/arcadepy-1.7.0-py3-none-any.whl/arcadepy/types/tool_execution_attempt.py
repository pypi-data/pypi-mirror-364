# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .shared.authorization_response import AuthorizationResponse

__all__ = ["ToolExecutionAttempt", "Output", "OutputError", "OutputLog"]


class OutputError(BaseModel):
    message: str

    additional_prompt_content: Optional[str] = None

    can_retry: Optional[bool] = None

    developer_message: Optional[str] = None

    retry_after_ms: Optional[int] = None


class OutputLog(BaseModel):
    level: str

    message: str

    subtype: Optional[str] = None


class Output(BaseModel):
    authorization: Optional[AuthorizationResponse] = None

    error: Optional[OutputError] = None

    logs: Optional[List[OutputLog]] = None

    value: Optional[object] = None


class ToolExecutionAttempt(BaseModel):
    id: Optional[str] = None

    finished_at: Optional[str] = None

    output: Optional[Output] = None

    started_at: Optional[str] = None

    success: Optional[bool] = None

    system_error_message: Optional[str] = None
