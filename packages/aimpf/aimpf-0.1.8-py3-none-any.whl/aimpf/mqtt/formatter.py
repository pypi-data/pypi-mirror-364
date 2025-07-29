from datetime import datetime, timezone
from pycarta.mqtt.formatter import Formatter, JSONFormatter
from shortuuid import uuid
import json


class CamxFormatter(Formatter):
    def __init__(self,
                 *,
                 projectLabel,
                 assetId: str,
                 dataItemId: str,
                 operatorId: str):
        self.projectLabel = str(projectLabel)
        self.assetId = str(assetId)
        self.dateTime = None
        self.dataItemId = str(dataItemId)
        self.operatorId = str(operatorId)

    def pack(self, data) -> bytes:
        return json.dumps({
                "projectLabel": self.projectLabel,
                "assetId": self.assetId,
                "dateTime": datetime.now(timezone.utc).isoformat(),
                "dataItemId": self.dataItemId,
                "value": data,
                "operatorId": self.operatorId,
                "messageId": uuid()
            }).encode("utf-8")
    
    def unpack(self, payload: bytes):
        # Modifies formatter settings based on content read.
        content = json.loads(payload.decode("utf-8"))
        self.projectLabel = content["projectLabel"]
        self.assetId = content["assetId"]
        self.dateTime = datetime.fromisoformat(content["dateTime"])
        self.dataItemId = content["dataItemId"]
        self.operatorId = content["operatorId"]
        return content["value"]
