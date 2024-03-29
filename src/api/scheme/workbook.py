from typing import List, Optional, Union, Tuple, Any, Dict

import re

from collections import Counter

from pydantic import BaseModel, root_validator

from src.api.handler import SchemeHandler


class Format(BaseModel):
    """
    Описание форматирования значения
    """
    formatter: str
    options: List[str]
    output:Optional[Dict[str, str]]
    attribute:Optional[str]

class Document(BaseModel):
    """
    Описание объекта в документе
    """
    regex: str
    index: int = 0 # значение по умолчанию, до момента расчета текущего индекса
    optional: bool
    format: Optional[List[Format]]


class Mapping(BaseModel):
    """
    Описание соответствия значение <-> код
    """
    input: str
    link: str
    output: str


class Database(BaseModel):
    """
    Описание соответствующей модели ORM и атрибута модели, в который передается значение объекта Column
    """
    orm: str
    params:Optional[Dict[str, str]]
    format:Optional[List[Format]]


class Column(BaseModel):
    """ 
    Столбец с указанием признаков для текстового поиска и создания объектов из найденных результатов
    """
    name: str
    document: Document
    mapping: Optional[List[Mapping]] = None
    database: Optional[Database] = None


class HeaderAttribute(BaseModel):
    name: str
    optional: bool

class Workbook(BaseModel):
    """ 
    Корневой объект описывающий документ колоночного типа (Excel)

    """
    title: str
    name: str
    sheet: str
    header: Optional[List[HeaderAttribute]]
    columns: List[Column]


    def update_column(self, name: str, value: dict):
        """
        Обновление записи колонки

        Args:
            name (str): наименование атрибута
            value (dict): [description]

        Raises:
            ValueError: отсутствует столбец с таким именем
        """
        # поиск в массиве по name или index
        try:
            column = next(c for c in self.columns if c.name == name)
        except StopIteration:
            raise ValueError('Не найдена запись для обновления')
        else:
            column.dict().update(value)
            return self

    def delete_column(self, name: str):
        """

        удаление столбца

        Args:
            name (str): наименование столбца

        Raises:
            ValueError: столбец с таким именем не найден
        """
        try:
            idx, _ = next((idx, c) for idx, c in enumerate(self.columns)
                          if c.name == name)
        except StopIteration:
            raise ValueError('Не найдена запись для удаления')
        else:
            self.columns.pop(idx)
        return self

    def add_column(self, name: str, value: dict):
        try:
            column = Column(name=name, **value)
        except:
            raise ValueError('Ошибка изменения записи')
        else:
            self.columns.append(column)

    def delete_attribute(self, name:str):
        """
        delete_attribute 

        удаление атрибута заголовка

        Args:
            name (str): наименование атрибута
        """
        if self.header:
            try:
                idx, _ = next((idx, h) for idx, h in enumerate(self.header)
                            if h.name == name)

            except StopIteration:
                raise ValueError('Не найдена запись для удаления')
            else:
                self.header.pop(idx)
            return self




    def verify_columns(
        self, source: Tuple[Any, ...]
    ) -> Tuple[Union['Workbook', None], List[Any], List[Any], List[Any]]:
        """

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
            match:Union[Column, None] = next((c for c in self.columns
                          if re.match(c.document.regex, value)), None)
            if match:
                match.document.index = idx 
                matched.append(match)
        missing_required = [
            c.name for c in self.columns
            if not c in matched and not c.document.optional
        ]
        missing_optional = [
            c.name for c in self.columns
            if not c in matched and c.document.optional
        ]
        # если количество совпадений соответствует кол-ву аргументов, то считать, что схема найдена
        # в ином случае полагать что, схема документа не описана
        if len(matched) == len(source):
            schema = self
        return schema, matched, missing_required, missing_optional

    def validate_columns(self, schema: Union[str, None], matched: list,
                         missing_required: list, missing_optional: list):
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
            duplicates = [
                item
                for item, count in Counter([m.name for m in matched]).items()
                if count > 1
            ]
            if duplicates:
                raise ValueError(
                    f'Дублирование столбцов, документ не отвечает требованиям схемы. {duplicates}'
                )
        else:
            raise ValueError('Схема документа не найдена')
        output = {
            'schema': schema,
            'columns': [m.dict() for m in matched],
            'missing': {
                'required': missing_required,
                'optional': missing_optional
            }
        }
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
    def write(cls, scheme: str, data: dict) -> None:
        return super().dump(scheme, data, ensure_exists=False)

__all__ =['WorkbookSchemes', 'Workbook', 'Column', 'HeaderAttribute']