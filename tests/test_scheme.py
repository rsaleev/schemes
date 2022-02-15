import os 

import pytest


@pytest.fixture(autouse=True, scope='session') 
def mock_test_env():
    os.environ['SCHEMES_PATH'] = "/home/rost/Development/GIS_OK/schemes/data"


def test_erot_match(mock_test_env):
    from src.api.scheme.workbook import WorkbookSchemes

    headers = [
        '№ п/п', 'ID требования', 'Содержание обязательного требования',
        'Статус публикации', 'Дата публикации', 'Статус работы с требованием',
        'Уровень регулирования',
        'Реквизиты структурной единицы акта, содержащего обязательное требование',
        'Текст структурной единицы акта, содержащей обязательное требование',
        'Срок действия обязательного требования',
        'Статус обязательного требования',
        'Объект, к которому предъявляются обязательные требования',
        'Категории лиц, обязанных соблюдать обязательное требование',
        'Иные категории лиц, обязанных соблюдать обязательное требование',
        'Форма оценки соблюдения обязательного требования',
        'Вид государственного контроля (надзора) или разрешительной деятельности',
        'Орган, ответственный за внесение сведений',
        'Орган, проверяющий соответствие обязательному требованию',
        'Проверочный вопрос', 'Вид акта', 'Название акта', 'Текст акта',
        'Утвердивший орган', 'Дата утверждения акта', 'Номер акта', 'ID акта',
        'Гиперссылка на текст акта (www.pravo.gov.ru)',
        'Наименование акта, устанавливающего ответственность за несоблюдение обязательного требования',
        'Статья акта, устанавливающая ответственность за несоблюдение обязательного требования',
        'Часть статьи акта, устанавливающей ответственность за несоблюдение обязательного требования',
        'Текст структурной единицы акта, устанавливающей ответственность за несоблюдение обязательного требования',
        'Органы власти, привлекающие к ответственности за несоблюдение обязательного требования',
        'Субъект ответственности за несоблюдение обязательного требования',
        'Ответственность для физического лица',
        'Размер/длительность санкции для физического лица',
        'Комментарии для физического лица',
        'Ответственность для индивидуального предпринимателя',
        'Размер/длительность санкции для индивидуального предпринимателя',
        'Комментарии для индивидуального предпринимателя',
        'Ответственность для юридического лица',
        'Размер/длительность санкции для юридического лица',
        'Комментарии для юридического лица',
        'Ответственность для должностного лица',
        'Размер/длительность санкции для должностного лица',
        'Комментарии для должностного лица',
        'Сферы общественных отношений, затрагиваемые обязательным требованием',
        'Виды экономической деятельности лиц, обязанных соблюдать обязательное требование',
        'Оценка затрат лиц, в отношении которых устанавливается обязательное требование, на его исполнение, а также информация об уровне причиненного охраняемым законом ценностям вреда (ущерба)',
        'Перечень документов (сведений), подтверждающих соответствие субъекта (объекта) обязательному требованию',
        'Орган, осуществляющий выдачу документов или предоставление сведений, подтверждающих соответствие субъекта (объекта) обязательному требованию',
        'Иные органы, осуществляющие выдачу документов или предоставление сведений, подтверждающих соответствие субъекта (объекта) обязательному требованию',
        'Гиперссылки на утвержденные проверочные листы (при наличии)',
        'Гиперссылки на руководства по соблюдению обязательных требований (при наличии)',
        'Гиперссылки на доклады о достижении целей введения обязательных требований (при наличии)',
        'GUID', 'Ссылка'
    ]
    schemes = WorkbookSchemes.read()
    erot_scheme = next(scheme for scheme in schemes if scheme.name =='erot')
    assert erot_scheme.name == 'erot'
    result_verified = erot_scheme.verify_columns(tuple(headers))
    assert len(result_verified) == 4
    assert result_verified[0] 
    assert result_verified[0].name == 'erot'
    assert result_verified[1]

    result_validated = erot_scheme.validate_columns(result_verified[0].name, result_verified[1], result_verified[2], result_verified[3]) 
    assert result_validated
    assert result_validated['columns']
    assert isinstance(result_validated['columns'], list)
    assert all([col['document']['index'] > 0 for col in result_validated['columns']])

