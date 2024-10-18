import uuid

from fastapi import Request
from ufaas_fastapi_business.routes import AbstractAuthRouter

from .models import Product
from .schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema


class ProductsRouter(AbstractAuthRouter[Product, ProductSchema]):
    def __init__(self):
        super().__init__(model=Product, schema=ProductSchema, user_dependency=None)

    def config_routes(self, **kwargs):
        super().config_routes(**kwargs)

    async def list_items(self, request: Request):
        return await super().list_items(request, 0, 10)

    async def create_item(self, request: Request, data: ProductCreateSchema):
        await super().create_item(request, data.model_dump())

    async def update_item(
        self, request: Request, uid: uuid.UUID, data: ProductUpdateSchema
    ):
        return await super().update_item(
            request, uid, data.model_dump(exclude_none=True)
        )


router = ProductsRouter().router
