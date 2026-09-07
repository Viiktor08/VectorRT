from fastapi import APIRouter, HTTPException

from app.models.attacks import PortScanRequest, PortScanResponse
from app.services.nmap_service import ScanTimeoutError, TargetNotAllowedError, run_port_scan

router = APIRouter(prefix="/api/attacks", tags=["attacks"])


@router.post("/port-scan", response_model=PortScanResponse)
async def port_scan(request: PortScanRequest) -> PortScanResponse:
    try:
        result = await run_port_scan(str(request.target_ip))
    except TargetNotAllowedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ScanTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    return PortScanResponse(**result)
