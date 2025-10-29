import os

from fastapi import Request
from fastapi_mongo_base.utils import usso_routes
from usso import APIHeaderConfig, AuthConfig, UserData
from usso.integrations.fastapi import USSOAuthentication

from .models import Product
from .schemas import ProductCreateSchema, ProductSchema, ProductUpdateSchema


class ProductsRouter(usso_routes.AbstractTenantUSSORouter):
    model = Product
    schema = ProductSchema

    async def get_user(self, request: Request, **kwargs: object) -> UserData:
        usso_base_url = os.getenv("USSO_BASE_URL") or "https://usso.uln.me"

        usso = USSOAuthentication(
            jwt_config=AuthConfig(
                jwks_url=(f"{usso_base_url}/.well-known/jwks.json"),
                api_key_header=APIHeaderConfig(
                    header_name="x-api-key",
                    verify_endpoint=(f"{usso_base_url}/api/sso/v1/apikeys/verify"),
                ),
            ),
            from_usso_base_url=usso_base_url,
            raise_exception=False,
        )
        return usso(request)

    async def retrieve_item(self, request: Request, uid: str) -> Product:
        item = await self.get_item(uid=uid)
        return item

    async def create_item(self, request: Request, data: ProductCreateSchema) -> Product:
        return await super().create_item(request, data.model_dump())

    async def update_item(
        self, request: Request, uid: str, data: ProductUpdateSchema
    ) -> Product:
        return await super().update_item(
            request, uid, data.model_dump(exclude_none=True)
        )


router = ProductsRouter().router
