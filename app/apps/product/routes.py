import uuid

from fastapi import Request
from fastapi_mongo_base.utils import usso_routes

from .models import Product
from .schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema


class ProductsRouter(usso_routes.AbstractTenantUSSORouter):
    model = Product
    schema = ProductSchema

    async def create_item(self, request: Request, data: ProductCreateSchema) -> Product:
        await super().create_item(request, data.model_dump())

    async def update_item(
        self, request: Request, uid: uuid.UUID, data: ProductUpdateSchema
    ) -> Product:
        return await super().update_item(
            request, uid, data.model_dump(exclude_none=True)
        )


router = ProductsRouter().router
