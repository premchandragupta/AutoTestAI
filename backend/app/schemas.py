
from pydantic import BaseModel
from typing import Optional

class DocumentCreate(BaseModel):
    filename: str
    content: str
    user_id: Optional[int] = None
