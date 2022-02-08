from abc import abstractmethod
import os

import json

from typing import Dict, Any, List

import json


class SchemeHandler(type):
    """ 

    Обработчик для загрузки, сохранения данных в формате JSON

    """

    PATH:str

    SOURCE:str 

    def __init_subclass__(cls) -> None:
        cls.PATH  = f'{os.environ["SCHEMES_PATH"]}'
        super().__init_subclass__()

    @classmethod
    def load(cls) -> List[Dict[str, Any]]:
        """load 

        Загрузка данных из нескольких документов в указанной директории, соответствующих расширению .json
            file (str): путь к файлу

        Returns:
           List[Dict[str, Any]]: возвращает массив структур dict
        """
        pathname = f'{cls.PATH}/{cls.SOURCE}'
        schemes = []
        for filename in os.listdir(pathname):
            _, tail = os.path.splitext(filename)
            if tail == '.json':
                with open(f'{pathname}/{filename}', 'r', encoding='utf8') as f:
                    schemes.append(json.loads(f.read(-1)))
        return schemes
        
    
    @classmethod
    def dump(cls, scheme:str, data:dict, ensure_exists=True) -> None:
        """dump 

        Загрузка данных в файл *.json в соответствие

        Args:
            source (str): тип данных documents/database/...
            scheme (str): наименование схемы -> имя файла
            data (dict): данные для записи
            ensure_exists (bool, optional): если записывается новая схема, то проверка не производится, 
                                            если идет обновление существующей, то проверка осуществляется. 
                                            Defaults to True.
        Raises:
            FileNotFoundError: [description]
        """
        filename = f'{cls.PATH}/{cls.SOURCE}/{scheme}.json'
        if ensure_exists:
            if not os.path.isfile(filename):
                raise FileNotFoundError
        with open(filename, 'w', encoding='utf8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True))

    @classmethod
    def read(cls, *args, **kwargs):
        """read 

        Методы для подклассов

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    @classmethod
    def update(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def write(cls, *args, **kwargs):
        raise NotImplementedError