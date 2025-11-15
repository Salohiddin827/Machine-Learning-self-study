from pydantic import BaseModel
from typing import List

class ActionsResponse(BaseModel):
    actions: List[str]