from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EmailCreate(BaseModel):
    addresses: list[str]