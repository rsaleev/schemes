from typing import Union,Optional, Union, List


from enum import Enum

from dataclasses import asdict

from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from pydantic import BaseModel,ValidationError, validator, root_validator
from starlette.types import Message

from src.service.models import scheme
from src.core.schemes import WorkbookSchemes

router = APIRouter(tags=['schemes', 'scheme'])


@router.get('/schemes/{source}', response_model=scheme.SchemeResponse, response_model_exclude_unset=True, description='Получить массив всех схем документов')
async def fetch_schemes(source:scheme.SchemeSource):
    if source == scheme.SchemeSource.documents:
        schemes = WorkbookSchemes.load()
        return JSONResponse(status_code=200, content=scheme.SchemeResponse(data=schemes).dict())
    if source == scheme.SchemeSource.database:
        # TODO implement
        return JSONResponse(status_code=204, content=scheme.SchemeResponse(status='OK').dict(exclude_unset=True))
    else:
        raise HTTPException(status_code=400, detail='Неверный запрос')
    # no data
    return JSONResponse(status_code=404, content={})

@router.get('/scheme/{source}/{name}', response_model=scheme.SchemeResponse, description='Получить схему в соответствие с типом источника и названием')
async def fetch_scheme(source:scheme.SchemeSource, name:str):
    """fetch_scheme 

    Получение схемы по типу источника и имени

    Args:
        source (SchemeSource): [description]
        name (str): [description]

    Returns:
        [type]: [description]
    """
    if source == scheme.SchemeSource.documents:
        workbook_schemes = WorkbookSchemes.load()
        wb_scheme_match = next((s for s in workbook_schemes if s.name == name), None)
        if wb_scheme_match:
            return scheme.SchemeResponse(content=)
    if source == scheme.SchemeSource.database:
        return JSONResponse(status_code=200, content={})
    return JSONResponse(status_code=404, content={})

@router.post('/scheme/{source}/{name}', response_model=scheme.SchemeResponse, description='Обновить схему документа по названию')
async def modify_scheme(source:scheme.SchemeSource, name:str, scheme_request:scheme.SchemeRequest):
    """modify_scheme 

    Args:
        source (SchemeSource): тип источника данных document/database/...
        name (str): наименование схемы
        scheme (Scheme): данные схемы в формате JSON

    Returns:
        [type]: [description]
    """
    if source == scheme.SchemeSource.documents:
        schemes = WorkbookSchemes.load()
        scheme_match = next((s for s in schemes if s.name == name), None)
        if not scheme_match:
            return JSONResponse(status_code=404, content={})
        try:
            column = None 
            if scheme_request.index:
                column = next((col for col in scheme_match.header.elements if col.index == scheme_request.index), None)
            elif scheme_request.name:
                column = next((col for col in scheme_match.header.elements if col.index == scheme_request.index), None)
            if column:
                asdict(column).update(scheme_request.dict(exclude_unset=True))
                WorkbookSchemes.dump(scheme_match.name, asdict(scheme_match))
            else:
                return JSONResponse(status_code=404, content={'status':"Not exists"})
        except:
            return JSONResponse(status_code=500, content={'status':'Error', 'message':'Operational'})
        else:
            return JSONResponse(status_code=200, content={'status':'OK'})

