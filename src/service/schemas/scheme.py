

from typing import Optional, List, Union, Dict

from enum import Enum

from pydantic import BaseModel

from src.api.schemes import Workbook



class SchemeDataType(str, Enum):
    """SchemeDataType 

    Описание структуры документа или модели в БД
   
    """
    documents = "documents"
    database = "database"

class SchemeHeaderElement(str, Enum):
    """SchemeHeaderElement
    Описание элементов в заголовке структуру документа или модели в БД

    """
    column  = "column"
    attribute = "attribute"

class SchemeColumnRequest(BaseModel):

    name:str
    index:Optional[int]
    regex:Optional[str]
    optional:Optional[bool]  
    
class SchemeResponse(BaseModel):
    data:Optional[Union[Workbook, List[Workbook]]]
    error:Optional[str]

class ValidationResponse(BaseModel):
    data:Optional[Dict]
    error:Optional[str]