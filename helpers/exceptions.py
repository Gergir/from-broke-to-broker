from fastapi import HTTPException


def raise_404_not_found(error: str = "Entity not found") -> None:
    raise HTTPException(status_code=404, detail=error)


def raise_400_bad_request(error: str = "Bad request") -> None:
    raise HTTPException(status_code=400, detail=error)
