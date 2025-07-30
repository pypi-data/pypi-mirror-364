from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class MessageSchema(BaseModel):
    arbId: Optional[str] = ""
    name: str
    networkName: str = ""
    ecuName: Optional[str] = ""
    ecuId: Optional[str] = ""
    fileId: Optional[str] = ""
    messageDate: Optional[str] = ""
    requestCode: Optional[str] = ""

    @classmethod
    def from_variables(cls, variables):
        name = variables.get("messageName") or variables["name"]
        message_date = variables.get("messageDate", "")
        if isinstance(message_date, float) or isinstance(message_date, int):
            message_date = datetime.utcfromtimestamp(message_date).isoformat() + "Z"

        return cls(
            arbId=variables.get("arbId", ""),
            name=name,
            networkName=variables.get("networkName", ""),
            ecuName=variables.get("ecuName", ""),
            ecuId=variables.get("ecuId", ""),
            fileId=variables.get("fileId", ""),
            messageDate=message_date,
            requestCode=variables.get("requestCode", ""),
        )

    def cache_key(self) -> str:
        return f"{self.name}|{self.networkName}|{self.ecuName}|{self.arbId}"
