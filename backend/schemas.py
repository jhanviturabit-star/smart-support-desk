from pydantic import BaseModel
from typing import Optional, List

class Customer(BaseModel):
    c_id : int
    c_name : str
    c_email : str
    phone : Optional[int]
    