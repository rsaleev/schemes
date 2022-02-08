from typing import List, Optional, Union, Dict, Tuple, Type, Any, TypeVar

import re

from collections import Counter

from pydantic import BaseModel, ValidationError, root_validator, validator

from src.api.handler import SchemeHandler


class Attribute(BaseModel):
    """ 
    Атрибут, включающий в себя указание на конкретную позицию Y-index в столбцах
    """
    name: str
    index: Optional[int]
    optional: bool
class Format(BaseModel):
    formatter:str
    options:List[str]

class Column(BaseModel):
    """ 
    Столбец с указанием признаков для текстового поиска и создания объектов из найденных результатов
    """
    name: str
    index:Optional[int] = 0 
    regex:str 
    optional:bool
    format:Union[List[Format], None]
   
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

class Workbook(BaseModel):
    """ 
    Корневой объект описывающий документ колоночного типа (Excel)

    """
    title:str
    name: str
    sheet:str
    header: Header

    @root_validator
    def validate_header(cls, values):
        if not 'header' in values:
            raise ValueError(
                'В схеме отстутствует описание заголовка листа Excel')
        return values

    def update_column(self, name:str, value: dict):
        """
        update_column [summary]

        [extended_summary]

        Args:
            name (str): [description]
            value (dict): [description]

        Raises:
            ValueError: отсутствует столбец с таким именем
        """
        # поиск в массиве по name или index
        try:
            column = next(c for c in self.header.columns if c.name == name)
        except StopIteration:
            raise ValueError('Не найдена запись для обновления')
        else:
            column.dict().update(value)
            return self

    def delete_column(self, name:str):
        """
        delete_column 

        удаление столбца

        Args:
            name (str): наименование столбца

        Raises:
            ValueError: столбец с таким именем не найден
        """
        try:
            idx,_ = next((idx,c) for idx,c in enumerate(self.header.columns) if c.name == name)
        except StopIteration:
            raise ValueError('Не найдена запись для удаления')
        else:
            self.header.columns.pop(idx)

    def add_column(self, name:str, value:dict):
        try:
            column = Column(name=name, **value)
        except:
            raise ValueError('Ошибка изменения записи')
        else:
            self.header.columns.append(column)


    def verify_columns(self, source: Tuple[Any, ...]) -> Tuple[Union['Workbook', None], List[Any], List[Any], List[Any]]:
        """
        verify_columns 

        Проверка наличия в заголовке наименований столбцов

        Args:
            source (tuple): строка с ячейками

        Returns:
            [type]: [description]
        """
        schema = None
        matched = []
        for idx, value in enumerate(source, start=1):
            # поиск по совпадению регулярного значения и исходного заголовка. Возвращает None если не найдено значение
            match = next((c for c in self.header.columns if re.match(c.regex, fr"{value}")),None)
            if match:
                match.index = idx
                matched.append(match)
        missing_required = [c.name for c in self.header.columns if not c in matched and not c.optional]
        missing_optional = [c.name for c in self.header.columns if not c in matched and c.optional]
        # если количество совпадений соответствует кол-ву аргументов, то считать, что схема найдена
        # в ином случае полагать что, схема документа не описана
        if len(matched) == len(source):
            schema = self
        return schema, matched, missing_required, missing_optional

    def validate_columns(self, schema: Union[str, None], matched: list, missing_required: list, missing_optional:list):
        """
        validate_columns 

        Валидация с проверкой на дубли

        Args:
            schema (Union[str, None]): [description]
            matched (list): [description]
            missing_required (list): [description]
            missing_optional (list): [description]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            [type]: [description]
        """
        if schema:
            duplicates = [item for item, count in Counter(
                [m.name for m in matched]).items() if count > 1]
            if duplicates:
                raise ValueError(
                    f'Дублирование столбцов, документ не отвечает требованиям схемы. {duplicates}')
            # if unmatched:
            #     raise ValueError(
            #         f'Отсутствуют обязательные столбцы {";".join(unmatched)}')
        else:
            raise ValueError('Схема документа не найдена')
        output = {'schema': schema, 'columns':[m.dict() for m in matched], 'missing':{'required':missing_required, 'optional':missing_optional}}
        return output


class WorkbookSchemes(SchemeHandler):

    SOURCE = 'documents'

    @classmethod
    def read(cls):       
        return [Workbook(**data) for data in super().load()]
    
    @classmethod
    def update(cls, scheme: str, data: dict) -> None:
        return super().dump(scheme, data, ensure_exists=True)

    @classmethod
    def write(cls, scheme: str, data: dict)->None:
        return super().dump(scheme, data, ensure_exists=False)