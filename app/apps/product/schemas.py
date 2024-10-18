import uuid
from decimal import Decimal
from enum import Enum
from typing import Any, Literal

from fastapi_mongo_base._utils.bsontools import decimal_amount
from fastapi_mongo_base.schemas import BusinessOwnedEntitySchema
from pydantic import BaseModel, field_validator
from server.config import Settings
from utils.aionetwork import aio_request


class Bundle(BaseModel):
    asset: str
    quota: Decimal
    order: Literal[0, 1, 2] = 1
    unit: str = "unit"

    @field_validator("quota", mode="before")
    def validate_quota(cls, value):
        return decimal_amount(value)


class ItemType(str, Enum):
    saas_package = "saas_package"
    retail_product = "retail_product"


class ProductSchema(BusinessOwnedEntitySchema):
    name: str
    description: str | None = None
    unit_price: Decimal
    currency: str = Settings.currency
    # quantity: Decimal = Decimal(1)

    # Item type to distinguish between SaaS and e-commerce
    item_type: ItemType = ItemType.retail_product  # Default to e-commerce product

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

    variant: dict[str, str] | None = None

    # Optional additional data field for future extensions or custom data
    extra_data: dict | None = None

    @field_validator("unit_price")
    def validate_price(cls, value):
        return decimal_amount(value)

    @field_validator("quantity")
    def validate_quantity(cls, value):
        return decimal_amount(value)

    async def validate_product(self):
        if self.validation_url is None:
            return True

        validation_data = await aio_request(method="GET", url=self.validation_url)
        if validation_data.get("price") != self.unit_price:
            return False

        if validation_data.get("stock_quantity") is None:
            return True

        if validation_data.get("stock_quantity") < self.quantity:
            return False

        return True

    async def reserve_product(self):
        if self.reserve_url is None:
            return

        await aio_request(method="POST", url=self.reserve_url, json=self.model_dump())

    async def webhook_product(self):
        if self.webhook_url is None:
            return

        await aio_request(method="POST", url=self.webhook_url, json=self.model_dump())


class ProductCreateSchema(BaseModel):
    name: str
    description: str | None = None
    unit_price: Decimal
    currency: str = Settings.currency
    quantity: Decimal = Decimal(1)
    variant: dict[str, str] | None = None

    webhook_url: str | None = None

    revenue_share_id: uuid.UUID | None = None
    tax_id: str | None = None
    merchant: str | None = None

    meta_data: dict[str, Any] | None = None
    data: dict | None = None


class ProductUpdateSchema(BaseModel):
    name: str
    description: str | None = None
    unit_price: Decimal
    currency: str = Settings.currency
    quantity: Decimal = Decimal(1)
    variant: dict[str, str] | None = None

    webhook_url: str | None = None

    revenue_share_id: uuid.UUID | None = None
    tax_id: str | None = None
    merchant: str | None = None

    meta_data: dict[str, Any] | None = None
    data: dict | None = None
