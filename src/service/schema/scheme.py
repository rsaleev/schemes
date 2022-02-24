from typing import Optional, Union, List
from pydantic import BaseModel

from enum import Enum
from src.api.scheme.workbook import HeaderAttribute

from src.api.scheme.workbook import * 



class SchemeElementType(Enum):
    column = 'column'
    header = 'header'


class SchemeColumnRequest(Column):
    pass

    class Meta:
        arbitrary_type_allowed = True

class SchemeHeaderRequest(HeaderAttribute):
    pass

    class Meta:
        arbitrary_type_allowed = True

class SchemeResponse(BaseModel):
    data:Optional[Union[Workbook, List[Workbook]]]
    error:Optional[str]

__all__ = ['SchemeElementType', 'SchemeHeaderRequest', 'SchemeResponse', 'SchemeColumnRequest']