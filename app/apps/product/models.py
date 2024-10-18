from fastapi_mongo_base.models import BusinessOwnedEntity

from .schemas import ProductSchema


class Product(ProductSchema, BusinessOwnedEntity):
    class Settings:
        indexes = BusinessOwnedEntity.Settings.indexes

    # @property
    # def product_url(self):
    #     return self.item_url
