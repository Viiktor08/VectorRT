from pydantic import BaseModel, IPvAnyAddress


class PortScanRequest(BaseModel):
    target_ip: IPvAnyAddress


class PortScanResponse(BaseModel):
    target_ip: str
    command: str
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
