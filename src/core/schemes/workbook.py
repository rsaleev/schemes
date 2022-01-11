from typing import List, Optional, Union, Dict

import re

from collections import Counter

from pydantic import BaseModel, root_validator

from src.core.handler import SchemeHandler




class Attribute(BaseModel):
    """ 
    Атрибут, включающий в себя указание на конкретную позицию Y-index в столбцах
    """

    name: str
    index: int
    optional: bool
    

class Format(BaseModel):
    formatter:str
    options:List[str]


class Column(BaseModel):
    """ 
    Столбец с указанием признаков для текстового поиска и создания объектов из найденных результатов
    """
    name: str
    model:str
    model_attribute:str
    regex: str
    optional: bool
    index: int
    output:List[str]
    format:Union[List[Format], None]
    mapping:str 


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

    def _delete_column(self, name:str) -> None:
        """_delete_column 

        Удаление столбца из массива по параметру column.name

        Args:
            name (str): имя объекта

        Raises:
            ValueError: возвращается если объект не найден
        """

        try:
            result: Column = next(
                c for c in self.columns if c.name == name)
        except StopIteration:
            raise ValueError
        else:
            self.columns.remove(result)

    def _delete_attribute(self,name:str) -> None:
        if self.attributes:
            try:
                result:Attribute = next(a for a in self.attributes if a.name == name)
            except StopIteration:
                raise ValueError
            else:
                self.attributes.remove(result)

    def _add_column(self, value: dict):
        self.columns.append(Column(**value))

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

    def delete_column(self, column_name:str)->Dict[str, str]:
        self.header._delete_column(column_name)
        return self.dict()

    def delete_attribute(self, attribute_name:str):
        self.header._delete_attribute(attribute_name)
        return self.dict()

    def verify_columns(self, source: tuple):
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
        if schema:
            duplicates = [item for item, count in Counter(
                [m.name for m in matched]).items() if count > 1]
            if duplicates:
                raise ValueError(
                    'Дублирование столбцов, документ не отвечает требованиям схемы')
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