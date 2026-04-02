from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.clients.io_service import (
    create_list,
    delete_list,
    get_list_members,
    get_lists,
    get_user_by_email,
    share_list,
    update_list,
)
from app.dependencies import get_current_user
from app.schemas import (
    CreateListRequest,
    DeleteListResponse,
    ListResponse,
    ListMemberResponse,
    ShareListRequest,
    ShareListResponse,
    UpdateListRequest,
    ValidateTokenResponse,
)

router = APIRouter(tags=["lists"])


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list_endpoint(
    payload: CreateListRequest,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> ListResponse:
    created = await create_list(current_user.user_id, payload.name, payload.max_budget)
    return ListResponse.model_validate(created.model_dump())


@router.get("/lists", response_model=list[ListResponse])
async def get_lists_endpoint(
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> list[ListResponse]:
    items = await get_lists(current_user.user_id)
    return [ListResponse.model_validate(item.model_dump()) for item in items]


@router.patch("/lists/{list_id}", response_model=ListResponse)
async def update_list_endpoint(
    payload: UpdateListRequest,
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> ListResponse:
    updated = await update_list(
        list_id=list_id,
        owner_id=current_user.user_id,
        name=payload.name,
        max_budget=payload.max_budget,
    )
    return ListResponse.model_validate(updated.model_dump())


@router.delete("/lists/{list_id}", response_model=DeleteListResponse)
async def delete_list_endpoint(
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> DeleteListResponse:
    deleted = await delete_list(list_id=list_id, owner_id=current_user.user_id)
    return DeleteListResponse.model_validate(deleted.model_dump())


@router.post("/lists/{list_id}/share", response_model=ShareListResponse)
async def share_list_endpoint(
    payload: ShareListRequest,
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> ShareListResponse:
    invited_user = await get_user_by_email(payload.user_email)
    shared = await share_list(
        list_id=list_id,
        owner_id=current_user.user_id,
        user_id=invited_user.id,
        user_email=invited_user.email,
        role=payload.role,
    )
    return ShareListResponse.model_validate(shared.model_dump())


@router.get("/lists/{list_id}/members", response_model=list[ListMemberResponse])
async def get_list_members_endpoint(
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> list[ListMemberResponse]:
    members = await get_list_members(list_id=list_id, requester_id=current_user.user_id)
    return [ListMemberResponse.model_validate(item.model_dump()) for item in members]
