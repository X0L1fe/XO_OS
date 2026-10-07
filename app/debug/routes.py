from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/debug/echo")
async def echo(request: Request):
    body = await request.body()
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError:
        decoded = body.decode("utf-8", errors="replace")
    return {"body": decoded, "body_bytes": list(body)}