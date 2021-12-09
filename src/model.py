# generated by datamodel-codegen:
#   filename:  erot.scheme.json
#   timestamp: 2021-12-07T09:28:23+00:00

from __future__ import annotations

from typing import Optional, Any

from pydantic import BaseModel, Field

import re

class ErotExcelDocument(BaseModel):
    id: str = Field(..., description='№ п/п', regex='(?i)^№ п/п$')
    req_id: Optional[str] = Field(
        None, description='ID требования', regex='(?i)^id требования$'
    )


data =('тест','№ п/п')
erot = ErotExcelDocument(**{'id':'№ п/п'})
def create(input_data:tuple):
    output = ErotExcelDocument.construct(**{})
    for d in input_data:
        match = next((k for k,v in ErotExcelDocument.schema()['properties'].items() if re.match(v['pattern'], d)),None)
        if match:
            output.__setattr__(match, d)
    return output


