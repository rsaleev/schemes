from os import stat
from typing import Union,Optional, Union, List


from enum import Enum

from dataclasses import asdict

from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from pydantic import BaseModel,ValidationError, validator, root_validator
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_501_NOT_IMPLEMENTED
from starlette.types import Message
from src.core.schemes.workbook import Column, Workbook

from src.service.models import scheme
from src.core.schemes import WorkbookSchemes

router = APIRouter(tags=['schemes', 'scheme'])

@router.get('/schemes')
async def index():
    return 'OK'

@router.get('/schemes/{source}', response_model=List[Workbook], response_model_exclude_unset=True, description='Получить массив всех схем документов')
async def fetch_schemes(source:scheme.SchemeSource):
    """fetch_schemes 

    Получить все структуры документов

    Args:
        source (scheme.SchemeSource): тип источника данных document/database/...

    Raises:
        HTTPException: [description]

    Returns:
        JSON: структуры документов в формате JSON
    """
    if source == scheme.SchemeSource.documents:
        schemes = WorkbookSchemes.load()
        return schemes
    if source == scheme.SchemeSource.database:
        # TODO: реализовать получение списка моделей
        raise HTTPException(status_code=501, detail='Не реализовано')
   

@router.get('/schemes/{source}/{name}', response_model=Workbook,  response_model_exclude_unset=True, description='Получить схему в соответствие с типом источника и названием')
async def fetch_scheme(source:scheme.SchemeSource, name:str):
    """fetch_scheme 

    Получение схемы по типу источника и имени

    Args:
        source (SchemeSource): [description]
        name (str): [description]

    Returns:
        JSON: Возвращает схему в формате JSON
    """
    if source == scheme.SchemeSource.documents:
        workbook_schemes = WorkbookSchemes.load()
        try:
            wb_scheme_match = next(s for s in workbook_schemes if s.name == name)
        except StopIteration:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Схема не найдена')
        else:
            return wb_scheme_match
    if source == scheme.SchemeSource.database:
        # TODO: реализовать получение списка моделей
        raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail='Не реализовано')

@router.post('/schemes/{source}/{name}', description='Обновить элемент в схеме документа по названию', status_code=200)
async def modify_scheme_element(source:scheme.SchemeSource, name:str, scheme_request:scheme.SchemeRequest):
    """modify_scheme 

    Args:
        source (SchemeSource): тип источника данных document/database/...
        name (str): наименование схемы

    Returns:
        : [description]

    Raises:
        HTTPException
    """
    schemes = None
    if source == scheme.SchemeSource.documents:
        schemes = WorkbookSchemes.load()
    elif source == scheme.SchemeSource.database:
        raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail='')
    try:
        scheme_match:Workbook = next(s for s in schemes if s.name == name)
    except StopIteration:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Схема не найдена')
    else:
        data = scheme_match.update_column(scheme_request.dict(exclude_unset=True))
        WorkbookSchemes.dump(source, scheme_match.name, data)
        return scheme_match
  
@router.delete('/schemes/{source}/{name}', description='Удалить элемент в схеме документа по названию', status_code=200)
def delete_scheme_element(source:scheme.SchemeSource, name:str):
    """delete_scheme_element [summary]

    [extended_summary]

    Args:
        source (scheme.SchemeSource): [description]
        name (str): [description]
    """
    schemes = None
    if source == scheme.SchemeSource.documents:
        schemes = WorkbookSchemes.load()
    elif source == scheme.SchemeSource.database:
        raise HTTPException(status_code=HTTP_501_NOT_IMPLEMENTED, detail='')
     try:
        scheme_match:Workbook = next(s for s in schemes if s.name == name)
    except StopIteration:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Схема не найдена')
    else:
        data = scheme_match.update_column(scheme_request.dict(exclude_unset=True))
        WorkbookSchemes.dump(source, scheme_match.name, data)
        return scheme_match