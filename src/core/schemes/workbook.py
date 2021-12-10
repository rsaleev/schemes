import os

from typing import List, Optional, Union, Tuple, Dict

import re

from collections import Counter

from pydantic import BaseModel, root_validator
from pydantic.error_wrappers import ValidationError

from src.core.loader import SchemaLoader


class Attribute(BaseModel):
    """ 
    Атрибут, включающий в себя указание на конкретную позицию Y-index в столбцах
    """

    name: str
    index: int
    optional: bool


class Column(BaseModel):
    """ 
    Столбец с указанием признаков для текстового поиска и создания объектов из найденных результатов
    """
    name: str
    regex: str
    optional: bool
    index: Optional[int]


class Header(BaseModel):

    """ 
    Заголовок документа, включайщий в себя атрибуты, хранящиейся  в "ленивом" колоночном формате, 
    а также столбцы, составляющие структуру документа

    Пример:
        объединенные ячейки с наименованием документа, датой и т.п.

    """
    columns: List[Column] = []
    attributes: Optional[List[Attribute]]

    @root_validator
    def validate_columns(cls, values):
        if not 'columns' in values:
            raise ValueError(
                'В схеме отстутствует описание столбцов листа Excel')
        return values

    def _update_column(self, value: dict):
        try:
            result: Column = next(
                c for c in self.columns if c.name == value['name'])
        except:
            raise ValueError
        else:
            for k, v in value.items():
                result.__setattr__(k, v)

    def _update_attribute(self, value: dict) -> None:
        """_update_attribute 

        Обновление атрибута

        Args:
            value (dict): входные данные

        Raises:
            AttributeError: в случае отсутствия массива атрибутов у документа
            ValueError: в случае отсуствтвия совпадений по имени атрибута
        """
        if not self.attributes:
            raise AttributeError('Отсутствуют атрибуты заголовка')
        try:
            result: Attribute = next(
                a for a in self.attributes if a.name == value['name'])
        except:
            raise ValueError
        else:
            for k, v in value.items():
                result.__setattr__(k, v)

    def _delete_column(self, value: dict) -> None:

        try:
            result: Column = next(
                c for c in self.columns if c.name == value['name'])
        except:
            raise ValueError
        else:
            self.columns.remove(result)

    def _add_column(self, value: dict):
        self.columns.append(Column(**value))

    def _delete_attribute(self, value: dict) -> None:
        pass

    def _add_attribute(self, value: dict) -> None:
        if not self.attributes:
            raise AttributeError("Отсутствуют атрибуы заголовка")
        self.attributes.append(Attribute(**value))


class Workbook(BaseModel):
    """ 
    Корневой объект описывающий документ колоночного типа (Excel)

    """

    name: str
    header: Header

    @root_validator
    def validate_header(cls, values):
        if not 'header' in values:
            raise ValueError(
                'В схеме отстутствует описание заголовка листа Excel')
        return values

    def update_column(self, value: dict):
        """update_column 

        Изменение значений в объекте Column из массива

        Args:
            value (dict): [description]

        Raises:
            ValueError:

        Returns:
            [type]: [description]
        """
        # поиск в массиве по name или index
        try:
            self.header._update_column(value)
        except StopIteration:
            raise ValueError('Не найдена запись для обновления')
        else:
            return self.dict()

    def update_attribute(self, value: dict) -> Dict[str, str]:
        """update_attribute 

        Args:
            value (dict): [description]

        Raises:
            ValueError:

        Returns:
            dict: [description]
        """
        # поиск в массиве по name или index
        try:
            self.header._update_attribute(value)
            # изменение значений
        except StopIteration:
            raise ValueError('Не найдена запись для обновления')
        else:
            return self.dict()

    def delete_column(self, )

    def verify_columns(self, source: tuple):
        schema = None
        matched = []
        unmatched = []
        for idx, value in enumerate(source, start=1):
            # поиск по совпадению регулярного значения и исходного заголовка. Возвращает None если не найдено значение
            match = next(
                (c for c in self.header.columns if re.match(c.regex, value)), None)
            # при найденном значении меняет индекс положения по оси X
            if match:
                match.index = idx
                matched.append(match)
        unmatched.extend([c.name for c in self.header.columns if not c.name in [
                         m.name for m in matched] and not c.optional])
        # если количество совпадений соответствует кол-ву аргументов, то считать, что схема найдена
        # в ином случае полагать что, схема документа не описана
        if len(matched) == len(source):
            schema = self.name
        return (schema, matched, unmatched)

    def validate_columns(self, schema: Union[str, None], matched: list, unmatched: list):
        if schema:
            duplicates = [item for item, count in Counter(
                [m.name for m in matched]).items() if count > 1]
            if duplicates:
                raise ValueError(
                    'Дублирование столбцов, документ не отвечает требованиям схемы')
            if unmatched:
                raise ValueError(
                    f'Отсутствуют обязательные столбцы {";".join(unmatched)}')
        else:
            raise ValueError('Схема документа не найдена')
        return {'schema': schema, 'matched': matched, 'required': unmatched}


class WorkbookSchemes(SchemaLoader):

    @classmethod
    def load(cls):
        path = f'{os.environ["SCHEMES_PATH"]}/documents'
        schemes = []
        for file in os.listdir(path):
            _, tail = os.path.splitext(file)
            if tail == '.json':
                schemes.append(Workbook(**super().load(f'{path}/{file}')))
        return schemes
