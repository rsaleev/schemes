

from typing import Optional, List, Union, Dict

from enum import Enum

from pydantic import BaseModel

from src.api.scheme import *

class SchemeElement(str, Enum):
    """SchemeHeaderElement
    Описание элементов в заголовке структуру документа или модели в БД

    """
    column  = "column"
    attribute = "attribute"

class SchemeColumnRequest(Column):
    pass

    class Meta:
        arbitrary_type_allowed = True

class SchemeHeaderRequest(Header):
    pass

    class Meta:
        arbitrary_type_allowed = True

    
    
class SchemeResponse(BaseModel):
    data:Optional[Union[Workbook, List[Workbook]]]
    error:Optional[str]

class ValidationResponse(BaseModel):
    data:Optional[Dict]
    error:Optional[str]