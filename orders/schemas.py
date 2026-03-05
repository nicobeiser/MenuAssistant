from pydantic import BaseModel, Field
from typing import List, Optional

class OrderItemIn(BaseModel):
    dish_id: str
    title: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(gt=0)



# Lo que el cliente manda desde el front
class OrderCreateIn(BaseModel):
    items: List[OrderItemIn]
    table_id: Optional[str] = None


# Lo que va a responder la api
class OrderOut(BaseModel):
    id: int
    status: str
    amount: float
    table_id: Optional[str] = None
    items: list

    class Config:
        from_attributes = True