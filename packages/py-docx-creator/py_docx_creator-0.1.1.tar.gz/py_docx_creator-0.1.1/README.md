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
from py_docx_creator.CoreClasses import CoreDocumentCreator
from py_docx_creator.CustomClasses import MainPageFormat, MainDocumentWriter, HeaderParagraphFormat, MainTextStyle, \
    MainParagraphFormat


class DocumentAPI(CoreDocumentCreator):

    def __init__(self, file_name: str):
        super().__init__()
        self.file_name = file_name

    def run(self):
        self.create_document(self.file_name)
        MainPageFormat().apply_style(document=self.document)
        paragraph = MainDocumentWriter.add_paragraph_to_document(self.document)
        HeaderParagraphFormat().apply_style(paragraph=paragraph)
        run = MainDocumentWriter.add_run_to_paragraph(paragraph=paragraph, text="Какой либо текст")
        MainTextStyle().apply_style(run=run)

        paragraph = MainDocumentWriter.add_paragraph_to_document(self.document)
        MainParagraphFormat().apply_style(paragraph=paragraph)
        run = MainDocumentWriter.add_run_to_paragraph(paragraph=paragraph, text="Какой либо текст")
        MainTextStyle().apply_style(run=run)
        self.save_document()


if __name__ == '__main__':
    
    DocumentAPI("Документ.docx").run()
```



