from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    userId: int
    societyId: int
    buildingId: int
    flatId: int
    firstName: str
    lastName: str
    sex: Optional[str] = None
    status: int = 1
