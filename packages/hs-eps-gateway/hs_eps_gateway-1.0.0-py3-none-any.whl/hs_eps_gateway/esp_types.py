# eps_gateway/types.py

from typing import List, Optional
from pydantic import BaseModel

class ProductItem(BaseModel):
    ProductName: str
    NoOfItem: str
    ProductProfile: str
    ProductCategory: str
    ProductPrice: str
