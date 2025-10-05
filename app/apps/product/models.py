from fastapi_mongo_base.models import UserOwnedEntity

from .schemas import ProductSchema


class Product(ProductSchema, UserOwnedEntity):
    pass
