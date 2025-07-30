from typing import NewType
from pydantic import EmailStr, conint

EmailAddress = NewType("EmailAddress", EmailStr)
EmailID = NewType("EmailID", str)  

Limit = NewType("Limit", conint(ge=1, le=100))
Offset = NewType("Offset", conint(ge=0))
UnixTimestamp = NewType("UnixTimestamp", int)
Message = NewType("Message", str)
Subject = NewType("Subject", str)
HTMLContent = NewType("HTMLContent", str)
TextContent = NewType("TextContent", str)
