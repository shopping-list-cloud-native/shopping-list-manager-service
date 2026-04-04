from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.clients.budget_service import get_budget, recalculate_budget
from app.clients.io_service import (
    create_list,
    delete_list,
    get_list_members,
    get_lists,
    get_user_by_email,
    share_list,
    update_list,
    verify_list_access,
)
from app.clients.items_service import (
    create_item,
    delete_item,
    get_items,
    update_item,
)
from app.clients.notification_service import create_notification, get_notifications
from app.dependencies import get_current_user
from app.schemas import (
    CreateItemRequest,
    CreateListRequest,
    BudgetStatusResponse,
    DeleteItemResponse,
    DeleteListResponse,
    ItemResponse,
    ListResponse,
    ListMemberResponse,
    NotificationResponse,
    ShareListRequest,
    ShareListResponse,
    UpdateItemRequest,
    UpdateBudgetRequest,
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
    await create_notification(
        user_id=invited_user.id,
        list_id=list_id,
        message=f"Lista a fost partajata cu tine de {current_user.email}.",
    )
    return ShareListResponse.model_validate(shared.model_dump())


@router.get("/lists/{list_id}/members", response_model=list[ListMemberResponse])
async def get_list_members_endpoint(
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> list[ListMemberResponse]:
    members = await get_list_members(list_id=list_id, requester_id=current_user.user_id)
    return [ListMemberResponse.model_validate(item.model_dump()) for item in members]


@router.post("/lists/{list_id}/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    payload: CreateItemRequest,
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> ItemResponse:
    await verify_list_access(list_id=list_id, user_id=current_user.user_id)
    created = await create_item(
        list_id=list_id,
        name=payload.name,
        quantity=payload.quantity,
        estimated_price=payload.estimated_price,
        actor_user_id=current_user.user_id,
        actor_email=current_user.email,
    )
    return ItemResponse.model_validate(created.model_dump())


@router.get("/lists/{list_id}/items", response_model=list[ItemResponse])
async def get_items_endpoint(
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> list[ItemResponse]:
    await verify_list_access(list_id=list_id, user_id=current_user.user_id)
    items = await get_items(list_id=list_id)
    return [ItemResponse.model_validate(item.model_dump()) for item in items]


@router.patch("/lists/{list_id}/items/{item_id}", response_model=ItemResponse)
async def update_item_endpoint(
    payload: UpdateItemRequest,
    list_id: UUID,
    item_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> ItemResponse:
    await verify_list_access(list_id=list_id, user_id=current_user.user_id)
    updated = await update_item(
        list_id=list_id,
        item_id=item_id,
        name=payload.name,
        quantity=payload.quantity,
        estimated_price=payload.estimated_price,
        checked=payload.checked,
        actor_user_id=current_user.user_id,
        actor_email=current_user.email,
    )
    return ItemResponse.model_validate(updated.model_dump())


@router.delete("/lists/{list_id}/items/{item_id}", response_model=DeleteItemResponse)
async def delete_item_endpoint(
    list_id: UUID,
    item_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> DeleteItemResponse:
    await verify_list_access(list_id=list_id, user_id=current_user.user_id)
    deleted = await delete_item(list_id=list_id, item_id=item_id)
    return DeleteItemResponse.model_validate(deleted.model_dump())


@router.get("/lists/{list_id}/budget", response_model=BudgetStatusResponse)
async def get_budget_endpoint(
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> BudgetStatusResponse:
    await verify_list_access(list_id=list_id, user_id=current_user.user_id)
    budget = await get_budget(list_id)
    return BudgetStatusResponse.model_validate(budget.model_dump())


@router.get("/notifications", response_model=list[NotificationResponse])
async def get_notifications_endpoint(
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> list[NotificationResponse]:
    notifications = await get_notifications(current_user.user_id)
    return [NotificationResponse.model_validate(item.model_dump()) for item in notifications]


@router.patch("/lists/{list_id}/budget", response_model=BudgetStatusResponse)
async def update_budget_endpoint(
    payload: UpdateBudgetRequest,
    list_id: UUID,
    current_user: ValidateTokenResponse = Depends(get_current_user),
) -> BudgetStatusResponse:
    await update_list(
        list_id=list_id,
        owner_id=current_user.user_id,
        name=None,
        max_budget=payload.max_budget,
    )
    budget = await recalculate_budget(list_id)
    return BudgetStatusResponse.model_validate(budget.model_dump())
