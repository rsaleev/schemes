from typing import Tuple, List

import concurrent.futures

from fastapi.routing import APIRouter
from fastapi import Query, HTTPException, status
from starlette.responses import JSONResponse

from src.service.models import scheme

from src.core.schemes import WorkbookSchemes, Workbook

router = APIRouter(tags=['scheme', 'validation'])


@router.get('/validate/{source}', response_model=scheme.SchemeResponse, status_code=status.HTTP_200_OK)
async def validate_schema(source:scheme.SchemeSource, headers:Tuple[str, ...]=Query(...)):
    schemes = []
    if source == scheme.SchemeSource.documents:
        schemes.extend(WorkbookSchemes.load())
    elif source == scheme.SchemeSource.database:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
    # проверка загрузки схем
    if not schemes:
        return scheme.SchemeResponse(error='Схема не найдена')
    # проверка входных данных на совпадение с моделью заголовка документа
    columns_verifying_results = [s.verify_columns(headers) for s in schemes]
    result = next(cfr for cfr in columns_verifying_results if cfr[0])
    if not result:
        return scheme.SchemeResponse(error='Схема не найдена')
    # проверка на совпадение по схеме, значение отличное от None
    try:
        output = result.validate_columns(*result)
    except Exception as e:
        return scheme.SchemeResponse(error=str(e))
    else:
        return scheme.SchemeResponse(data=output)
            



