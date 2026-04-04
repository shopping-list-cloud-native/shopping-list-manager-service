from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class CreateListRequest(BaseModel):
    name: str
    max_budget: Decimal = Decimal("0")


class UpdateListRequest(BaseModel):
    name: str | None = None
    max_budget: Decimal | None = None


class ListResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    max_budget: Decimal
    created_at: datetime


class DeleteListResponse(BaseModel):
    message: str


class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: UUID
    email: str


class IoListResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    max_budget: Decimal
    created_at: datetime


class IoDeleteListResponse(BaseModel):
    message: str


class ShareListRequest(BaseModel):
    user_email: str
    role: Literal["owner", "editor", "viewer"] = "editor"


class ShareListResponse(BaseModel):
    list_id: UUID
    shared_with: str
    role: Literal["owner", "editor", "viewer"]


class IoUserResponse(BaseModel):
    id: UUID
    email: str


class ListMemberResponse(BaseModel):
    user_id: UUID
    email: str
    role: Literal["owner", "editor", "viewer"]
    created_at: datetime


class VerifyListAccessResponse(BaseModel):
    list_id: UUID
    user_id: UUID
    role: Literal["owner", "editor", "viewer"]


class CreateItemRequest(BaseModel):
    name: str
    quantity: int = 1
    estimated_price: Decimal = Decimal("0")


class UpdateItemRequest(BaseModel):
    name: str | None = None
    quantity: int | None = None
    estimated_price: Decimal | None = None
    checked: bool | None = None


class ItemResponse(BaseModel):
    id: UUID
    list_id: UUID
    name: str
    quantity: int
    estimated_price: Decimal
    checked: bool
    created_at: datetime
    updated_at: datetime


class DeleteItemResponse(BaseModel):
    message: str


class BudgetStatusResponse(BaseModel):
    list_id: UUID
    max_budget: Decimal
    current_total: Decimal
    remaining_budget: Decimal
    status: str


class UpdateBudgetRequest(BaseModel):
    max_budget: Decimal


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    list_id: UUID
    message: str
    read: bool
    created_at: datetime
