from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.schemas import AppDetails, GenerateResponse
from backend.services.generator import generate_test_suite

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("", response_model=GenerateResponse)
async def generate(details: AppDetails) -> GenerateResponse:
    try:
        suite, filename, mime_type, content = await generate_test_suite(details)
    except Exception as exc:
        message = str(exc)
        if "not configured" in message or "disabled" in message:
            raise HTTPException(status_code=503, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc

    return GenerateResponse(
        suite=suite,
        exportFilename=filename,
        exportMimeType=mime_type,
        exportContent=content,
    )
