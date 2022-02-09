from typing import List, Optional, Union, Dict

from pydantic import BaseModel

from fastapi.routing import APIRouter
from fastapi import HTTPException, status, Query

from src.api.scheme.workbook import *
from src.api import exceptions

from src.api.scheme import WorkbookSchemes
from src.service.schema.scheme import * 
from src.service.schema.validation import *

router = APIRouter(prefix='/documents', tags=['Схемы документов/excel'])


@router.get('',
            response_model=List[Workbook],
            response_model_exclude_unset=True,
            description='Получить все известные схемы',
            status_code=status.HTTP_200_OK)
async def fetch_all():
    document_schemes = WorkbookSchemes.load()
    return document_schemes


@router.get(
    '/{schema_name}',
    response_model=Workbook,
    response_model_exclude_unset=True,
    description='Получить схему в соответствие с типом источника и названием',
    status_code=status.HTTP_200_OK)
async def fetch_scheme(schema_name: str):
    """

    Получение схемы по типу источника и имени

    Args:
        name (str): наименование схемы

    Returns:
        JSON: Возвращает схему в формате JSON
    """
    workbook_schemes = WorkbookSchemes.read()
    try:
        wb_scheme_match = next(s for s in workbook_schemes
                               if s.name == schema_name)
    except StopIteration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Схема не найдена')
    else:
        return wb_scheme_match


@router.put('/{schema_name}',
            description='Обновить элемент в схеме документа по названию',
            status_code=200)
async def modify_scheme_element(schema_name: str,
                                scheme_request: SchemeColumnRequest):
    """modify_scheme 

    Args:
        source (SchemeSource): тип источника данных document/database/...
        name (str): наименование схемы

    Returns:
        : [description]

    Raises:
        HTTPException
    """

    schemes = WorkbookSchemes.read()
    try:
        scheme_match: Workbook = next(s for s in schemes
                                      if s.name == schema_name)
    except StopIteration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Схема не найдена')
    else:
        data = scheme_match.update_column(
            scheme_request.name,
            scheme_request.dict(exclude_unset=True, exclude={'name'}))
        WorkbookSchemes.update(scheme_match.name, data.dict())
        return


@router.delete('/{schema_name}/{element_type}/{element_name}',
               description='Удалить элемент в схеме документа по названию',
               status_code=200,
               response_model=SchemeResponse)
def delete_scheme_element(element_type: SchemeElementType, schema_name: str,
                          element_name: str):
    """
    
    Удаление элемента из массива 

    Args:
        name (str): наименование схемы

    Returns:
        type: None 

    Raises:
        HTTPException: код ошибки в формате HTTP с описанием

    """
    schemes = WorkbookSchemes.read()
    if not schemes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Схема не найдена')
    try:
        scheme_match: Workbook = next(s for s in schemes
                                      if s.name == schema_name)
    except StopIteration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Схема не найдена')
    else:
        if element_type.column:
            try:
                data = scheme_match.delete_column(element_name)
            except (AttributeError, ValueError) as e:
                return SchemeResponse(error=str(e))
            else:
                WorkbookSchemes.write(scheme_match.name, data.dict())
                return
        elif element_type.header:
            try:
                data = scheme_match.delete_attribute(element_name)
            except (AttributeError, ValueError) as e:
                return SchemeResponse(error=str(e))
            else:
                if data:
                    WorkbookSchemes.write(scheme_match.name, data.dict())
                    return


@router.post('/{scheme_name}',
             description='Создать новую схему',
             status_code=201,
             response_model=SchemeResponse)
def add_new_scheme(scheme_name: str, data: Workbook):
    try:
        WorkbookSchemes.update(scheme_name, data.dict())
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Ошибка сохранения данных')
    else:
        return


def validate_document_schema(headers: list):
    schemes = WorkbookSchemes.read()
    if not schemes:
        raise exceptions.SchemeNotLoaded("Ошибка загрузки данных")
    result = [s.verify_columns(tuple(headers)) for s in schemes]
    if not result:
        raise exceptions.SchemeNotFound("Схема не найдена")
    for r in result:
        if r[0]:
            return r[0].validate_columns(r[0].name, r[1], r[2], r[3])


@router.get('/{source}',
            status_code=status.HTTP_200_OK,
            response_model=ValidationResponse,
            response_model_exclude_unset=True)
async def validate_schema(headers: List[str] = Query(...)):
    if not headers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Не переданы параметы запроса')
    try:
        output = validate_document_schema(headers)
        return scheme.ValidationResponse(data=output)
    except Exception as e:
        return scheme.ValidationResponse(error=str(e))
