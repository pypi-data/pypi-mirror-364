from typing import List, Dict
from pydantic import BaseModel
from .email import Email, EmailDetails


class APIError(BaseModel):
    name: str
    message: str


class EmailListResponse(BaseModel):
    status: bool
    result: List[Email]


class EmailDetailsResponse(BaseModel):
    status: bool
    result: EmailDetails


class MessageResponse(BaseModel):
    status: bool
    result: Dict[str, str]


class ErrorResponse(BaseModel):
    status: bool
    error: APIError
