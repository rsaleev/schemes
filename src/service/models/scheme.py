from typing import Optional, List, Union

from enum import Enum

from pydantic import BaseModel, root_validator

from src.core.schemes import Workbook



class SchemeSource(str, Enum):
    documents = "documents"
    database = "database"

class SchemeRequest(BaseModel):

    name:Optional[str]
    index:Optional[int]
    regex:Optional[str]
    optional:Optional[bool]    
        
    @root_validator(pre=True)
    def validate_id_passed(cls, values):
        if not values.get('name', None) and not values.get('index', None) in values:
            raise ValueError("Должно быть указано одно из полей index или name")
        return values

class SchemeResponse(BaseModel):
    data:Optional[List[Workbook]]

