from typing import Union, Optional, Union, List

from fastapi.routing import APIRouter
from fastapi import HTTPException, status

from src.core.schemes.workbook import Attribute, Column, Workbook

from src.service.models import scheme
from src.core.schemes import WorkbookSchemes

router = APIRouter(prefix='/schemes',tags=['schemes'])


@router.get('/', response_model=List[Workbook], response_model_exclude_unset=True, 
            description='Получить все известные схемы', status_code=status.HTTP_200_OK)
async def fetch_all():
    document_schemes = WorkbookSchemes.load()
    return document_schemes


@router.get('/{source}', response_model=List[Workbook], response_model_exclude_unset=True,
            description='Получить массив всех схем документов', status_code=status.HTTP_200_OK)
async def fetch_schemes(source: scheme.SchemeDataType):
    """fetch_schemes 

    Получить все структуры документов

    Args:
        source (scheme.SchemeSource): тип источника данных document/database/...

    Raises:
        HTTPException: [description]

    Returns:
        JSON: структуры документов в формате JSON
    """
    if source == scheme.SchemeDataType.documents:
        schemes = WorkbookSchemes.read()
        return schemes
    elif source == scheme.SchemeDataType.database:
        # TODO: реализовать получение списка моделей
        raise HTTPException(status_code=501, detail='Не реализовано')


@router.get('/{source}/{schema_name}', response_model=Workbook,  response_model_exclude_unset=True, 
            description='Получить схему в соответствие с типом источника и названием', status_code=status.HTTP_200_OK)
async def fetch_scheme(source: scheme.SchemeDataType, schema_name: str):
    """fetch_scheme 

    Получение схемы по типу источника и имени

    Args:
        source (SchemeSource): [description]
        name (str): [description]

    Returns:
        JSON: Возвращает схему в формате JSON
    """
    if source == scheme.SchemeDataType.documents:
        workbook_schemes = WorkbookSchemes.read()
        try:
            wb_scheme_match = next(
                s for s in workbook_schemes if s.name == schema_name)
        except StopIteration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Схема не найдена')
        else:
            return wb_scheme_match
    if source == scheme.SchemeDataType.database:
        # TODO: реализовать получение списка моделей
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='Не реализовано')


@router.post('/{source}/{schema_name}', description='Обновить элемент в схеме документа по названию', status_code=200)
async def modify_scheme_element(source: scheme.SchemeDataType, schema_name: str, scheme_request: scheme.SchemeColumnRequest):
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
    if source == scheme.SchemeDataType.documents:
        schemes = WorkbookSchemes.read()
    if source == scheme.SchemeDataType.database:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='')
    if not schemes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Неверный источник данных')
    try:
        scheme_match: Workbook = next(s for s in schemes if s.name == schema_name)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Схема не найдена')
    else:
        data = scheme_match.update_column(
            scheme_request.dict(exclude_unset=True))
        WorkbookSchemes.update(scheme_match.name, data)
        return scheme_match


@router.delete('/{source}/{schema_name}/{element_type}/{element_name}', description='Удалить элемент в схеме документа по названию', status_code=200)
def delete_scheme_element(source: scheme.SchemeDataType, element_type: scheme.SchemeHeaderElement, schema_name: str, element_name: str):
    """delete_scheme_element
    
    Удаление элемента из массива 

    Args:
        source (scheme.SchemeSource): тип источника данных documents/database/...
        name (str): наименование схемы

    Returns:
        type: None 

    Raises:
        HTTPException: код ошибки в формате HTTP с описанием

    """
    schemes = None
    if source == scheme.SchemeDataType.documents:
        schemes = WorkbookSchemes.read()
    if source == scheme.SchemeDataType.database:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail='')
    if not schemes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Схема не найдена')
    try:
        scheme_match: Workbook = next(
            s for s in schemes if s.name == schema_name)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Схема не найдена')
    else:
        data = None
        if element_type == scheme.SchemeHeaderElement.column:
            try:
                data = scheme_match.delete_column(element_name)
            except (AttributeError, ValueError):
                pass
        if element_type == scheme.SchemeHeaderElement.attribute:
            try:
                data = scheme_match.delete_attribute(element_name)
            except (AttributeError, ValueError):
                pass
        if not data:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='Схема не найдена')
        else:
            WorkbookSchemes.write(scheme_match.name, data)
        return

@router.put('/{source}/{scheme_name}', description='Добавить элемент в схеме документа по названию', status_code=201)
def add_new_scheme(source:scheme.SchemeDataType, scheme_name:str, data:Workbook):
    if source == scheme.SchemeDataType.documents:
        try:
            WorkbookSchemes.update(scheme_name, data.dict())
        except:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибка сохранения данных')
    else:
        raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Ошибка сохранения данных')