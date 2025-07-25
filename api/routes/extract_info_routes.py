from fastapi import APIRouter, HTTPException
from api.schemas.extract_info_schema import ExtractInfoRequest, ExtractInfoResponse
from api.services.extract_info_service import call_openai

router = APIRouter()


@router.post("/extract-info", response_model=ExtractInfoResponse)
async def extract_info(request: ExtractInfoRequest):
    try:
        result = await call_openai(request.messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
