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



class DishCreateIn(BaseModel):
    name: str
    description: str = ""
    price: float = 0.0
    category: str = "Sin categoría"
    image_url: str = ""
    available: bool = True
    tags: list[str] = []
    extraction_confidence: float | None = None
    extraction_source: str | None = None

class DishBulkIn(BaseModel):
    dishes: List[DishIn]



class DishUpdateIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.0
    category: Optional[str] = None
    image_url: Optional[str] = None
    available: bool = True
    tags: Optional[list[str]] = None
    extraction_confidence: Optional[float] = None
    extraction_source: Optional[str] = None