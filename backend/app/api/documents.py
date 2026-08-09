from fastapi import APIRouter, HTTPException, Query, Response

from app.services.qrcode import svg


router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("/qrcode.svg")
def qrcode_svg(
    value: str = Query(min_length=1, max_length=80),
) -> Response:
    try:
        contenu = svg(value.strip())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return Response(
        content=contenu,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )
