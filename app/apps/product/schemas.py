import uuid
from decimal import Decimal
from enum import StrEnum
from typing import Literal

import httpx
from fastapi_mongo_base.schemas import TenantUserEntitySchema
from fastapi_mongo_base.utils.bsontools import decimal_amount
from pydantic import BaseModel, ConfigDict, field_validator

from server.config import Settings


class Bundle(BaseModel):
    asset: str
    quota: Decimal
    order: Literal[0, 1, 2] = 1
    unit: str | None = None
    meta_data: dict | None = None

    model_config = ConfigDict(allow_inf_nan=True)

    @field_validator("quota", mode="before")
    @classmethod
    def validate_quota(cls, value: Decimal) -> Decimal:
        return decimal_amount(value)


class ItemType(StrEnum):
    saas_package = "saas_package"
    retail_product = "retail_product"


class ProductStatus(StrEnum):
    active = "active"
    inactive = "inactive"
    expired = "expired"
    deleted = "deleted"
    trial = "trial"


class ProductSchema(TenantUserEntitySchema):
    name: str
    description: str | None = None
    unit_price: Decimal
    currency: str = Settings.currency
    quantity: Decimal = Decimal(1)  # Stock quantity

    # Item type to distinguish between SaaS and e-commerce
    item_type: ItemType = ItemType.retail_product  # Default to e-commerce product
    variant: str | None = None

    product_url: str | None = None
    webhook_url: str | None = None
    reserve_url: str | None = None
    validation_url: str | None = None

    revenue_share_id: uuid.UUID | None = None
    tax_id: str | None = None
    merchant: str | None = None

    # SaaS-specific fields
    plan_duration: int | None = None  # Only for SaaS packages
    bundles: list[Bundle] | None = None  # Optional field for SaaS packages

    # Optional additional data field for future extensions or custom data
    # extra_data: dict | None = None

    status: ProductStatus = ProductStatus.active

    model_config = ConfigDict(allow_inf_nan=True)

    @field_validator("unit_price", mode="before")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        return decimal_amount(value)

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value: Decimal) -> Decimal:
        return decimal_amount(value)

    async def validate_product(self) -> bool:
        if self.validation_url is None:
            return True

        async with httpx.AsyncClient() as client:
            response = await client.get(self.validation_url)
            response.raise_for_status()
            validation_data: dict = response.json()

        if validation_data.get("price") != self.unit_price:
            return False

        if validation_data.get("stock_quantity") is None:
            return True

        return not validation_data.get("stock_quantity") < self.quantity

    async def reserve_product(self) -> None:
        if self.reserve_url is None:
            return

        async with httpx.AsyncClient() as client:
            await client.post(self.reserve_url, json=self.model_dump())

    async def webhook_product(self) -> None:
        if self.webhook_url is None:
            return

        async with httpx.AsyncClient() as client:
            await client.post(self.webhook_url, json=self.model_dump())


class ProductCreateSchema(BaseModel):
    name: str
    description: str | None = None
    unit_price: Decimal
    currency: str = Settings.currency
    # quantity: Decimal = Decimal(1)
    variant: str | None = None
    item_type: ItemType = ItemType.retail_product  # Default to e-commerce product

    webhook_url: str | None = None

    revenue_share_id: uuid.UUID | None = None
    tax_id: str | None = None
    merchant: str | None = None

    meta_data: dict[str, object] | None = None
    data: dict | None = None


class ProductUpdateSchema(BaseModel):
    name: str
    description: str | None = None
    unit_price: Decimal
    currency: str = Settings.currency
    quantity: Decimal = Decimal(1)
    variant: str | None = None

    webhook_url: str | None = None

    revenue_share_id: uuid.UUID | None = None
    tax_id: str | None = None
    merchant: str | None = None

    meta_data: dict[str, object] | None = None
    data: dict | None = None
