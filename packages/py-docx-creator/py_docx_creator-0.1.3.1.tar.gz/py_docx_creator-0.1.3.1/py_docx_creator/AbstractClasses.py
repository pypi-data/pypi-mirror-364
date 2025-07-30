from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from docx.document import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from docx.styles.styles import Styles
from docx.text.paragraph import Paragraph
from docx.text.run import Run


# region _________________Перечни для подстановки_________________

class FontNames(Enum):
    """Перечень наименований шрифтов"""
    TimesNewRoman = "Times New Roman"


class DocumentStyles(Enum):
    """Перечень стилей документа"""
    Normal = "Normal"


@dataclass
class AlignParagraph:
    LEFT: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.LEFT
    CENTER: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.CENTER
    RIGHT: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.RIGHT
    JUSTIFY: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.JUSTIFY
    DISTRIBUTE: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.DISTRIBUTE
    JUSTIFY_MED: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.JUSTIFY_MED
    JUSTIFY_HI: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.JUSTIFY_HI
    JUSTIFY_LOW: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.JUSTIFY_LOW
    THAI_JUSTIFY: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.THAI_JUSTIFY


# endregion _________________Перечни для подстановки_________________

# region _________________Управление документом_________________

class DocumentCreator(ABC):
    """Класс для создания, чтения, записи документа"""

    def __init__(self):
        self._file_name: str | None = None
        self._path_to_document: str | None = None
        self._document: Document | None = None

    @abstractmethod
    def create_document(self, file_name: str) -> None:
        """Создание документа"""
        pass

    @abstractmethod
    def load_document(self) -> None:
        """Загрузка уже имеющегося документа"""
        pass

    @abstractmethod
    def save_document(self) -> None:
        """Сохранение документа"""
        pass

    @property
    def file_name(self) -> str | None:
        return self._file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        self._file_name = value

    @property
    def path_to_document(self) -> str | None:
        return self._path_to_document

    @path_to_document.setter
    def path_to_document(self, value: str) -> None:
        self._path_to_document = value

    @property
    def document(self) -> Document:
        return self._document

    @document.setter
    def document(self, value: Document) -> None:
        self._document = value


class DocumentWriter(ABC):
    """Класс для наполнения документа"""

    @staticmethod
    @abstractmethod
    def add_paragraph_to_document(document: Document) -> Paragraph | None:
        """Добавление параграфа в документ"""
        pass

    @staticmethod
    @abstractmethod
    def add_run_to_paragraph(paragraph: Paragraph, text: str) -> Run | None:
        """Добавить текст в параграф"""
        pass

    @staticmethod
    @abstractmethod
    def add_page_break(document: Document) -> None:
        """Добавление разрыва страницы в документ"""
        pass


class DocumentStyle(ABC):
    """Стиль документа"""

    def __init__(self):
        self._document_style: str | None = None

    @property
    def document_style(self) -> str | None:
        """Стиль документа"""
        return self._document_style

    @document_style.setter
    def document_style(self, value: str) -> None:
        """Стиль документа"""
        self._document_style = value

    @abstractmethod
    def get_document_style(self, document: Document) -> Styles | None:
        """Получение стиля документа"""
        pass


# endregion _________________Управление документом_________________

# region _________________Стили_________________

@dataclass
class TextStyle(ABC):
    """
    Стиль текста.

    Атрибуты:
        size ( Pt | None): # размер шрифта

        name ( str | None): # наименование шрифта

        bold ( bool | None): # жирное начертание шрифта

        italic ( bool | None): # курсивное начертание шрифта

        underline ( bool | None): # подчеркнутое начертание шрифта

    """

    size: Pt | None  # размер шрифта
    name: str | None  # наименование шрифта
    bold: bool | None  # жирное начертание шрифта
    italic: bool | None  # курсивное начертание шрифта
    underline: bool | None  # подчеркнутое начертание шрифта


@dataclass
class PageStyle(ABC):
    """
    Стиль страницы.

        Атрибуты:
            top_margin ( Pt | None): # отступ сверху

            bottom_margin ( Pt | None): # отступ снизу

            left_margin ( Pt | None): # отступ слева

            right_margin ( Pt | None): # отступ справа

    """

    top_margin: Pt | None  # отступ сверху
    bottom_margin: Pt | None  # отступ снизу
    left_margin: Pt | None  # отступ слева
    right_margin: Pt | None  # отступ справа


@dataclass
class ParagraphStyle(ABC):
    """
    Стиль форматирования параграфа.

    Атрибуты:
        alignment (AlignParagraph | None): Выравнивание текста (влево, по центру, по ширине и т.п.).

        space_after (Pt | None): Отступ после параграфа.

        space_before (Pt | None): Отступ перед параграфом.

        left_indent (Inches | None): Отступ от левого края страницы.

        right_indent (Inches | None): Отступ от правого края страницы.

        line_spacing (float | None): Межстрочный интервал.

        first_line_indent (Pt | None): Отступ первой строки (красная строка).

        page_break_before (bool | None): Разрыв страницы перед параграфом.
    """

    alignment: AlignParagraph | None  # выравнивание
    space_after: Pt | None  # отступ до параграфа
    space_before: Pt | None  # отступ после параграфа
    left_indent: Inches | None  # отступ от левого края
    right_indent: Inches | None  # отступ от правого края
    line_spacing: float | None  # межстрочный интервал
    first_line_indent: Pt | None  # отступ красной строки
    page_break_before: bool | None  # разрыв страницы перед параграфом


# endregion _________________Стили_________________

# region _________________Управление стилями_________________
class PageStyleManager(ABC):
    @staticmethod
    @abstractmethod
    def apply_style(document: Document, style: PageStyle) -> None:
        """Применение стиля"""
        pass


class TextStyleManager(ABC):
    @staticmethod
    @abstractmethod
    def apply_style(run: Run, style: TextStyle) -> None:
        """Применение стиля"""
        pass


class ParagraphStyleManager(ABC):
    @staticmethod
    @abstractmethod
    def apply_style(paragraph: Paragraph, style: ParagraphStyle) -> None:
        """Применение стиля к параграфу"""
        pass


# endregion _________________Управление стилями_________________

# region _________________Централизированное управление менеджерами_________________

@dataclass
class StyleManager(ABC):
    PAGE_STYLE_MANAGER: PageStyleManager
    TEXT_STYLE_MANAGER: TextStyleManager
    PARAGRAPH_STYLE_MANAGER: ParagraphStyleManager
# endregion _________________Централизированное управление менеджерами_________________
