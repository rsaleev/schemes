from typing import Optional, Dict

from pydantic import BaseModel



class ValidationResponse(BaseModel):
    data:Optional[Dict]
    error:Optional[str]