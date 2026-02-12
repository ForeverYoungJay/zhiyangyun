from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name_zh: str
    code: str


class SpuCreate(BaseModel):
    category_id: str
    name_zh: str
    subtitle_zh: str = ""
    description_zh: str = ""


class SpuStatusUpdate(BaseModel):
    status: str = Field(pattern="^(draft|on_shelf|off_shelf)$")


class SkuCreate(BaseModel):
    spu_id: str
    sku_name_zh: str
    sku_code: str
    sale_price: float = 0
    warning_stock: int = 0
    available_stock: int = 0


class InventoryChangeCreate(BaseModel):
    sku_id: str
    quantity: int = Field(gt=0)
    remark: str = ""


class InventoryCheckCreate(BaseModel):
    sku_id: str
    actual_stock: int = Field(ge=0)
    remark: str = ""


class OrderItemCreate(BaseModel):
    sku_id: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    elder_id: str
    items: list[OrderItemCreate]


class OrderActionCreate(BaseModel):
    reason: str = ""
