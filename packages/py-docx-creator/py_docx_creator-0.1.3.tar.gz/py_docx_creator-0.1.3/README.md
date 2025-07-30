# DocxP

**DocxP** — это мой небольшой Python-проект для создания и форматирования Word-документов с использованием библиотеки `python-docx`.
Вы можете дополнять и расширять ее при необходимости. Я постарался построить гибкую основу для последующего расширения.


## Возможности

- Абстрактные классы для описания стилей документа, абзацев и текста.
- Реализация базовых стилей и логики генерации Word-документов.
- Гибкая настройка шрифтов, отступов, выравнивания и др.

## Структура проекта

- `py_docx_creator/`      — модуль с основными и абстрактными классами:
  - `AbstractClasses.py`  — абстрактные интерфейсы
  - `CoreClasses.py`      — реализация базовых стилей
  - `CustomClasses.py`    — расширение с пользовательскими стилями

## Установка

```bash
pip install python-docx py_docx_creator
```

## Пример использования

```python
from py_docx_creator.CoreClasses import CoreDocumentCreator, CoreStyleManager
from py_docx_creator.CustomClasses import MainPageStyle, MainTextStyle, HeaderParagraphStyle, \
    MainParagraphStyle, HeaderTextStyle, FastWriter


class DocumentAPI(CoreDocumentCreator):

    def __init__(self, file_name: str):
        super().__init__()
        self.file_name = file_name
        self.style_manager = CoreStyleManager
        self.write_to_document = FastWriter

    def run(self):
        self.create_document(self.file_name)

        self.style_manager.PAGE_STYLE_MANAGER.apply_style(self.document, MainPageStyle)

        self.write_to_document.write(document=self.document,
                                     text="Заголовок документа",
                                     text_style=HeaderTextStyle,
                                     paragraph_style=HeaderParagraphStyle)

        self.write_to_document.write(document=self.document,
                                     text="Основной текст 1",
                                     text_style=MainTextStyle,
                                     paragraph_style=MainParagraphStyle)

        self.save_document()


if __name__ == '__main__':
    DocumentAPI("Документ.docx").run()

```
## Пример создания собственных стилей

### 1. Создания стиля для параграфа

Пример создание собственного стиля параграфа на основе базового класса ` CoreParagraphStyle `.

```python

from dataclasses import dataclass

from py_docx_creator.CoreClasses import CoreParagraphStyle
from py_docx_creator.AbstractClasses import AlignParagraph
from docx.shared import Pt, Inches

@dataclass
class YourClass(CoreParagraphStyle):
    alignment: AlignParagraph | None    = None      # выравнивание                      |   AlignParagraph.*.value
    space_after: Pt | None              = None      # отступ до параграфа               |   Pt(int) 
    space_before: Pt | None             = None      # отступ после параграфа            |   Pt(int) 
    left_indent: Inches | None          = None      # отступ от левого края             |   Inches(float | int) 
    right_indent: Inches | None         = None      # отступ от правого края            |   Inches(float | int) 
    line_spacing: float | None          = None      # межстрочный интервал              |   float
    first_line_indent: Pt | None        = None      # отступ красной строки             |   Pt(int) 
    page_break_before: bool | None      = None      # разрыв страницы перед параграфом  |   bool

```
Поля, которые изменяться не будут указывать **не нужно** (исключить из `dataclass`).

### 2. Создание стиля для текста

Пример создания стиля текста на основе базового класса `CoreTextStyle`.

```python

from dataclasses import dataclass

from py_docx_creator.CoreClasses import CoreTextStyle
from docx.shared import Pt

@dataclass
class YourClass(CoreTextStyle):
    size: Pt | None                  = None      # размер шрифта текста             | Pt(int)
    name: str | None                 = None      # наименование шрифта              | str | FontNames.*.value
    bold: bool | None                = None      # жирное начертание шрифта         | bool
    italic: bool | None              = None      # курсивное начертание шрифта      | bool
    underline: bool | None           = None      # подчеркнутое начертание шрифта   | bool

```
Поля, которые изменяться не будут указывать **не нужно** (исключить из `dataclass`).

### 3. Создание стиля страниц документа

Пример создания стиля страниц документа на основе базового класса `CorePageStyle`.

```python

from dataclasses import dataclass

from py_docx_creator.CoreClasses import CorePageStyle
from docx.shared import Pt

@dataclass
class YourClass(CorePageStyle):
    top_margin: Pt | None        = None   # отступ сверху   | Pt(int)
    bottom_margin: Pt | None     = None   # отступ снизу    | Pt(int)
    left_margin: Pt | None       = None   # отступ слева    | Pt(int)
    right_margin: Pt | None      = None   # отступ справа   | Pt(int)

```

Поля, которые изменяться не будут указывать **не нужно** (исключить из `dataclass`).

### На данный момент доступно несколько заранее прописанных  стилей 
1. [x] `MainPageStyle` - стиль страниц документа с заданными полями;
2. [x] `MainParagraphStyle` - стиль параграфа для основного текста (теста по ширине, красная строка и др.);
3. [x] `HeaderParagraphStyle` - стиль параграфа для заголовков (текст по центру);





*Проект находится в активной разработке.*

 *IN PROGRESS:*

**[████████████░░░░░░░░░░░░░░░░░░░░░░░░] 25%** 

