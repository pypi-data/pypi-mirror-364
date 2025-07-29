from typing import List, Optional

from pydantic import BaseModel


class SignalSchema(BaseModel):
    configurationId: int
    messageId: int
    name: str
    unit: str
    paramType: Optional[str] = ""
    paramId: Optional[str] = ""
    signalType: Optional[str] = ""
    data: List[dict]

    @classmethod
    def from_variables(cls, config_id, message_id, batch, variables):
        return cls(
            configurationId=config_id,
            messageId=message_id,
            name=variables["name"],
            paramId=variables.get("paramId", ""),
            paramType=variables.get("paramType", ""),
            signalType=variables.get("signalType", ""),
            unit=variables["unit"],
            data=batch,
        )
