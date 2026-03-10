from typing import List, Optional
from pydantic import BaseModel, Field


class DishIn(BaseModel):
    name: str
    description: Optional[str] = ""
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    available: bool = True
    tags: List[str] = Field(default_factory=list)
    extraction_confidence: Optional[float] = None
    extraction_source: Optional[str] = None


class DishBulkIn(BaseModel):
    dishes: List[DishIn]