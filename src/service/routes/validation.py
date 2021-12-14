from typing import Tuple, List


from fastapi.routing import APIRouter
from fastapi import Query, HTTPException, status

from src.service.models import scheme

from src.core.schemes import WorkbookSchemes, Workbook, Column


router = APIRouter(prefix='/validate', tags=['validation'])


@router.get('/{source}',status_code=status.HTTP_200_OK, response_model=scheme.ValidationResponse, response_model_exclude_unset=True)
async def validate_schema(source:scheme.SchemeDataType, headers:List[str] = Query([])):
    schemes = []
    if source == scheme.SchemeDataType.documents:
        schemes.extend(WorkbookSchemes.read())
    elif source == scheme.SchemeDataType.database:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
    # проверка загрузки схем
    if not schemes:
        return scheme.ValidationResponse(error='Не удалось загрузить схемы')
    # проверка входных данных на совпадение с моделью заголовка документа
    columns_verifying_results = [s.verify_columns(headers) for s in schemes]
    try:
        result:Tuple[Workbook, List[Column], List[Column]] = next(cfr for cfr in columns_verifying_results if cfr[0])
    except StopIteration:
        return scheme.ValidationResponse(error='Схема не найдена')
    else:
        # проверка на совпадение по схеме, значение отличное от None
        try:
            output = result[0].validate_columns(result[0].name, result[1], result[2])
        except Exception as e:
            return scheme.ValidationResponse(error=str(e))
        else:
            return scheme.ValidationResponse(data=output)
                



