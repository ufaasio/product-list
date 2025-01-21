import uuid

from fastapi_mongo_base.models import BusinessOwnedEntity

from .schemas import ProductSchema


class Product(ProductSchema, BusinessOwnedEntity):
    class Settings:
        indexes = BusinessOwnedEntity.Settings.indexes

    @classmethod
    def get_query(
        cls,
        user_id: uuid.UUID = None,
        business_name: str = None,
        is_deleted: bool = False,
        *args,
        **kwargs,
    ):
        query = super().get_query(None, business_name, is_deleted, *args, **kwargs)
        return query

    # @property
    # def product_url(self):
    #     return self.item_url
