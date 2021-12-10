import os

import json
from typing import Callable, Dict

import aiofile

class SchemaLoader:

    @classmethod
    def load(cls, file:str) -> Dict[str, str]:
        """load 


        Args:
            file (str): путь к файлу

        Returns:
            Dict[str, str]: JSON -> Dict
        """
        with open(file, 'r') as f:
            return json.loads(f.read(-1))
    
    @classmethod
    def dump(cls, source:str, scheme:str, data:dict) -> None:
        file = f'{os.environ["SCHEMES_PATH"]}/{source}/{scheme}.json'
        if os.path.isfile(file):
            with open(file, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True))
        else:
            raise FileExistsError
           
