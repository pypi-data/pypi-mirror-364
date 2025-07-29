from abc import ABC, abstractmethod

from docx.document import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from docx.styles.styles import Styles
from docx.text.paragraph import Paragraph
from docx.text.run import Run


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
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def path_to_document(self):
        return self._path_to_document

    @path_to_document.setter
    def path_to_document(self, value):
        self._path_to_document = value

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, value):
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
    def document_style(self) -> str:
        """Стиль документа"""
        return self._document_style

    @document_style.setter
    def document_style(self, value) -> None:
        """Стиль документа"""
        self._document_style = value

    @abstractmethod
    def get_document_style(self, document: Document) -> Styles | None:
        """Получение стиля документа"""
        pass

class PageStyle(ABC):
    """Отступы от краев страницы"""

    def __init__(self):
        self._top_margin: Pt | None = None
        self._bottom_margin: Pt | None = None
        self._left_margin: Pt | None = None
        self._right_margin: Pt | None = None

    @abstractmethod
    def apply_style(self, document: Document) -> None:
        """Применение стиля"""
        pass

    @property
    def top_margin(self) -> Pt:
        """Отступ сверху"""
        return self._top_margin

    @top_margin.setter
    def top_margin(self, value: Pt) -> None:
        """Отступ сверху"""
        self._top_margin = value

    @property
    def bottom_margin(self) -> Pt:
        """Отступ снизу"""
        return self._bottom_margin

    @bottom_margin.setter
    def bottom_margin(self, value: Pt) -> None:
        """Отступ снизу"""
        self._bottom_margin = value

    @property
    def left_margin(self) -> Pt:
        """Отступ слева"""
        return self._left_margin

    @left_margin.setter
    def left_margin(self, value: Pt) -> None:
        """Отступ слева"""
        self._left_margin = value

    @property
    def right_margin(self) -> Pt:
        """Отступ справа"""
        return self._right_margin

    @right_margin.setter
    def right_margin(self, value: Pt) -> None:
        """Отступ справа"""
        self._right_margin = value

class TextStyle(ABC):
    """Стиль текста"""

    def __init__(self):
        self._font_size: Pt | None = None
        self._font_name: str | None = None
        self._text_bold: bool | None = None
        self._text_italic: bool | None = None
        self._text_underline: bool | None = None

    @abstractmethod
    def apply_style(self, run: Run) -> None:
        """Применение стиля"""
        pass

    @property
    def font_size(self) -> Pt:
        """Размер шрифта"""
        return self._font_size

    @font_size.setter
    def font_size(self, value: Pt) -> None:
        """Размер шрифта"""
        self._font_size = value

    @property
    def font_name(self) -> str:
        """Наименование шрифта"""
        return self._font_name

    @font_name.setter
    def font_name(self, value: str) -> None:
        """Наименование шрифта"""
        self._font_name = value

    @property
    def text_bold(self) -> bool:
        """Жирное начертание"""
        return self._text_bold

    @text_bold.setter
    def text_bold(self, value: bool) -> None:
        """Жирное начертание"""
        self._text_bold = value

    @property
    def text_italic(self) -> bool:
        """Курсивное начертание"""
        return self._text_italic

    @text_italic.setter
    def text_italic(self, value: bool) -> None:
        """Курсивное начертание"""
        self._text_italic = value

    @property
    def text_underline(self) -> bool:
        """Подчеркнутое начертание"""
        return self._text_underline

    @text_underline.setter
    def text_underline(self, value: bool) -> None:
        """Подчеркнутое начертание"""
        self._text_underline = value

class ParagraphStyle(ABC):

    def __init__(self):
        self._paragraph_alignment: WD_ALIGN_PARAGRAPH | None = None
        self._space_after_paragraph: Pt | None = None
        self._paragraph_left_indent: Inches | None = None
        self._paragraph_right_indent: Inches | None = None
        self._paragraph_line_spacing: float | None = None
        self._paragraph_first_line_indent: Pt | None = None

    @abstractmethod
    def apply_style(self, paragraph: Paragraph) -> None:
        """Применение стиля к параграфу"""
        pass

    @property
    def paragraph_alignment(self) -> WD_ALIGN_PARAGRAPH:
        """Выравнивание текста параграфа"""
        return self._paragraph_alignment

    @paragraph_alignment.setter
    def paragraph_alignment(self, value: WD_ALIGN_PARAGRAPH) -> None:
        """Выравнивание текста параграфа"""
        self._paragraph_alignment = value

    @property
    def space_after_paragraph(self) -> Pt:
        """Отступ после параграфа"""
        return self._space_after_paragraph

    @space_after_paragraph.setter
    def space_after_paragraph(self, value: Pt) -> None:
        """Отступ после параграфа"""
        self._space_after_paragraph = value

    @property
    def paragraph_left_indent(self) -> Inches:
        """Отступ слева от параграфа"""
        return self._paragraph_left_indent

    @paragraph_left_indent.setter
    def paragraph_left_indent(self, value: Inches) -> None:
        """Отступ слева от параграфа"""
        self._paragraph_left_indent = value

    @property
    def paragraph_right_indent(self) -> Inches:
        """Отступ справа от параграфа"""
        return self._paragraph_right_indent

    @paragraph_right_indent.setter
    def paragraph_right_indent(self, value: Inches) -> None:
        """Отступ справа от параграфа"""
        self._paragraph_right_indent = value

    @property
    def paragraph_line_spacing(self) -> float:
        """Межстрочный интервал параграфа"""
        return self._paragraph_line_spacing

    @paragraph_line_spacing.setter
    def paragraph_line_spacing(self, value: float) -> None:
        """Межстрочный интервал параграфа"""
        self._paragraph_line_spacing = value

    @property
    def paragraph_first_line_indent(self) -> Pt:
        """Отступ слева первой строки параграфа"""
        return self._paragraph_first_line_indent

    @paragraph_first_line_indent.setter
    def paragraph_first_line_indent(self, value: Pt) -> None:
        """Отступ слева первой строки параграфа"""
        self._paragraph_first_line_indent = value
