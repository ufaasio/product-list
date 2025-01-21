import uuid

from fastapi import Query, Request
from fastapi_mongo_base.core.exceptions import BaseHTTPException
from ufaas_fastapi_business.middlewares import (
    AuthorizationData,
    authorization_middleware,
)
from ufaas_fastapi_business.routes import AbstractAuthRouter

from .models import Product
from .schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema


class ProductsRouter(AbstractAuthRouter[Product, ProductSchema]):
    def __init__(self):
        super().__init__(model=Product, schema=ProductSchema, user_dependency=None)

    def config_routes(self, **kwargs):
        super().config_routes(**kwargs)

    async def get_auth(self, request: Request) -> AuthorizationData:
        auth = await authorization_middleware(request, anonymous_accepted=True)
        if auth.issuer_type == "User" and request.method != "GET":
            raise BaseHTTPException(401, "unauthorized", "Unauthorized")
        return auth

    async def list_items(
        self, request: Request, offset: int = Query(0), limit: int = Query(10)
    ):
        return await super().list_items(request, offset=offset, limit=limit)

    async def create_item(self, request: Request, data: ProductCreateSchema):
        await super().create_item(request, data.model_dump())

    async def update_item(
        self, request: Request, uid: uuid.UUID, data: ProductUpdateSchema
    ):
        return await super().update_item(
            request, uid, data.model_dump(exclude_none=True)
        )


router = ProductsRouter().router
