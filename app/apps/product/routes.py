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
        base_usso_url = os.getenv("BASE_USSO_URL") or "https://usso.uln.me"

        usso = USSOAuthentication(
            jwt_config=AuthConfig(
                jwks_url=(f"{base_usso_url}/.well-known/jwks.json"),
                api_key_header=APIHeaderConfig(
                    header_name="x-api-key",
                    verify_endpoint=(f"{base_usso_url}/api/sso/v1/apikeys/verify"),
                ),
            ),
            from_base_usso_url=base_usso_url,
            raise_exception=False,
        )
        return usso(request)

    async def create_item(self, request: Request, data: ProductCreateSchema) -> Product:
        return await super().create_item(request, data.model_dump())

    async def update_item(
        self, request: Request, uid: str, data: ProductUpdateSchema
    ) -> Product:
        return await super().update_item(
            request, uid, data.model_dump(exclude_none=True)
        )


router = ProductsRouter().router
