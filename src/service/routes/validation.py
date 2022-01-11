from typing import Tuple, List, Union


from fastapi.routing import APIRouter
from fastapi import Query, HTTPException, status

from src.service.models import scheme

from src.core.schemes import WorkbookSchemes, Column, Workbook

from src.core import exceptions

router = APIRouter(prefix='/validate', tags=['validation'])


async def validate_document_schema(headers: list):
    schemes = WorkbookSchemes.read()
    if not schemes:
        raise exceptions.SchemeNotLoaded("Не удалось загрузить схемы")
    result = [s.verify_columns(tuple(headers)) for s in schemes]
    for r in result:
        if r[0]:
            return r[0].validate_columns(r[0].name, r[1], r[2], r[3])
    raise exceptions.SchemeNotFound("Схема не найдена")




@router.get('/{source}', status_code=status.HTTP_200_OK, response_model=scheme.ValidationResponse, response_model_exclude_unset=True)
async def validate_schema(source: scheme.SchemeDataType, headers: List[str] = Query(...)):
    if not headers:
        return scheme.ValidationResponse(error="Не переданы значения заголовка")
    if source == scheme.SchemeDataType.documents:
        try:
            output = await validate_document_schema(headers)
            return scheme.ValidationResponse(data=output)
        except Exception as e:
            return scheme.ValidationResponse(error=str(e))
    elif source == scheme.SchemeDataType.database:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
  