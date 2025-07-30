from pydantic import BaseModel, EmailStr
from typing import Optional
from ..ctypes import EmailID, UnixTimestamp


class Email(BaseModel):
    id: EmailID
    from_address: EmailStr
    to_address: EmailStr
    subject: str
    received_at: UnixTimestamp


class EmailDetails(Email):
    html_content: Optional[str]
    text_content: Optional[str]
