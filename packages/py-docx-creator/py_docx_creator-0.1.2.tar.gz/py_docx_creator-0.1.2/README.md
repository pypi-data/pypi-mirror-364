# DocxP

**DocxP** — это мой небольшой Python-проект для создания и форматирования Word-документов с использованием библиотеки `python-docx`.
Вы можете дополнять и расширять ее при необходимости. Я постарался построить гибкую основу для последующего расширения.


## Возможности

- Абстрактные классы для описания стилей документа, абзацев и текста.
- Реализация базовых стилей и логики генерации Word-документов.
- Гибкая настройка шрифтов, отступов, выравнивания и др.

## Структура проекта

- `core/` — модуль с основными и абстрактными классами:
  - `AbstractClasses.py` — абстрактные интерфейсы
  - `CoreClasses.py` — реализация базовых стилей
  - `CustomClasses.py` — расширение с пользовательскими стилями

## Установка

```bash
pip install python-docx py_docx_creator
```

## Пример использования

```python
from py_docx_creator.CoreClasses import CoreDocumentCreator, CoreStyleManager
from py_docx_creator.CustomClasses import MainPageStyle, MainDocumentWriter, MainTextStyle, HeaderParagraphStyle, \
    MainParagraphStyle, HeaderTextStyle


class DocumentAPI(CoreDocumentCreator):

    def __init__(self, file_name: str):
        super().__init__()
        self.file_name = file_name
        self.style_manager = CoreStyleManager

    def run(self):
        self.create_document(self.file_name)
        self.style_manager.PAGE_STYLE_MANAGER.apply_style(self.document, MainPageStyle)

        paragraph = MainDocumentWriter.add_paragraph_to_document(self.document)
        self.style_manager.PARAGRAPH_STYLE_MANAGER.apply_style(paragraph, HeaderParagraphStyle)
        run = MainDocumentWriter.add_run_to_paragraph(paragraph=paragraph, text="Заголовок документа")
        self.style_manager.TEXT_STYLE_MANAGER.apply_style(run, HeaderTextStyle)

        paragraph = MainDocumentWriter.add_paragraph_to_document(self.document)
        self.style_manager.PARAGRAPH_STYLE_MANAGER.apply_style(paragraph, MainParagraphStyle)
        run = MainDocumentWriter.add_run_to_paragraph(paragraph=paragraph, text="Заголовок документа")
        self.style_manager.TEXT_STYLE_MANAGER.apply_style(run, MainTextStyle)

        self.save_document()


if __name__ == '__main__':
    DocumentAPI("Документ.docx").run()
```



