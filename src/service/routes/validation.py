from typing import Tuple, List

import concurrent.futures

from fastapi.routing import APIRouter
from fastapi import Query

from src.service.models import scheme

from src.core.schemes import WorkbookSchemes

router = APIRouter(tags=['scheme', 'validation'])



def background_validation(schemes:List[dict], data:Tuple[str, ...]):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(schemes)) as executor:
        results = {executor.submit(s.verify,*headers):s for s in schemes}
        for future in concurrent.futures.as_completed(results):

@router.get('/validate/{source}')
async def validate_schema(source:scheme.SchemeSource, headers:Tuple[str, ...]=Query(...)):
    if source == scheme.SchemeSource.documents:
        schemes = await WorkbookSchemes.load()
    
            



