from uuid import UUID

import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.schemas import (
    DeleteItemResponse,
    IoDeleteListResponse,
    IoListResponse,
    IoUserResponse,
    ItemResponse,
    ListMemberResponse,
    ShareListResponse,
    VerifyListAccessResponse,
)


def _serialize_decimal(value: str | int | float | None) -> str | int | float | None:
    if value is None:
        return None
    return str(value)


async def get_user_by_email(email: str) -> IoUserResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.get("/internal/users/by-email", params={"email": email})

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invited user not found",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to fetch user",
        )

    return IoUserResponse.model_validate(response.json())


async def create_list(owner_id: UUID, name: str, max_budget: str | int | float) -> IoListResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.post(
            "/internal/lists",
            json={
                "owner_id": str(owner_id),
                "name": name,
                "max_budget": _serialize_decimal(max_budget),
            },
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to create list",
        )

    return IoListResponse.model_validate(response.json())


async def get_lists(owner_id: UUID) -> list[IoListResponse]:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.get("/internal/lists", params={"owner_id": str(owner_id)})

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to fetch lists",
        )

    return [IoListResponse.model_validate(item) for item in response.json()]


async def update_list(
    list_id: UUID,
    owner_id: UUID,
    name: str | None,
    max_budget: str | int | float | None,
) -> IoListResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.patch(
            f"/internal/lists/{list_id}",
            json={
                "owner_id": str(owner_id),
                "name": name,
                "max_budget": _serialize_decimal(max_budget),
            },
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to update list",
        )

    return IoListResponse.model_validate(response.json())


async def delete_list(list_id: UUID, owner_id: UUID) -> IoDeleteListResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.request(
            "DELETE",
            f"/internal/lists/{list_id}",
            json={"owner_id": str(owner_id)},
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to delete list",
        )

    return IoDeleteListResponse.model_validate(response.json())


async def share_list(
    list_id: UUID,
    owner_id: UUID,
    user_id: UUID,
    user_email: str,
    role: str,
) -> ShareListResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.post(
            "/internal/list-members",
            json={
                "list_id": str(list_id),
                "owner_id": str(owner_id),
                "user_id": str(user_id),
                "user_email": user_email,
                "role": role,
            },
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )

    if response.status_code == status.HTTP_409_CONFLICT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this list",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to share list",
        )

    return ShareListResponse.model_validate(response.json())


async def get_list_members(list_id: UUID, requester_id: UUID) -> list[ListMemberResponse]:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.get(
            f"/internal/list-members/by-list/{list_id}",
            params={"requester_id": str(requester_id)},
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )

    if response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this list",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to fetch list members",
        )

    return [ListMemberResponse.model_validate(item) for item in response.json()]


async def verify_list_access(list_id: UUID, user_id: UUID) -> VerifyListAccessResponse:
    async with httpx.AsyncClient(base_url=settings.io_service_url, timeout=10.0) as client:
        response = await client.get(
            f"/internal/access/lists/{list_id}",
            params={"user_id": str(user_id)},
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )

    if response.status_code == status.HTTP_403_FORBIDDEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this list",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="IO service failed to verify list access",
        )

    return VerifyListAccessResponse.model_validate(response.json())
