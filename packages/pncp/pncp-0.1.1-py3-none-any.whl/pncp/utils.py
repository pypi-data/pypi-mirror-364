from typing import Any

import httpx


def get_many(url: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with httpx.Client(timeout=10) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_one(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(timeout=10) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()
