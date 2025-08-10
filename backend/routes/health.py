from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os

router = APIRouter()


@router.get("/health")
def health() -> JSONResponse:
    return JSONResponse(
        {
            "ok": True,
            "connectors": {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "gemini": bool(os.getenv("GEMINI_API_KEY")),
                "perplexity": bool(os.getenv("PERPLEXITY_API_KEY")),
            },
        }
    )