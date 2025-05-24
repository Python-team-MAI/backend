from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SendMailModel(BaseModel):
    addresses: list[str]
    subject: str
    message: str
