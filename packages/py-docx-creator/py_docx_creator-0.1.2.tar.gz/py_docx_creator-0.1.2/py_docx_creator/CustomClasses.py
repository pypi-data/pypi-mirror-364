from dataclasses import dataclass

from docx.shared import Pt, Inches

from py_docx_creator.AbstractClasses import DocumentStyles, FontNames
from py_docx_creator.CoreClasses import CoreDocumentStyle, CorePageStyle, \
    CoreTextStyle, CoreDocumentWriter, AlignParagraph, CoreParagraphStyle


class NormalDocumentStyle(CoreDocumentStyle):
    """Стандартный стиль документа"""

    def __init__(self):
        super().__init__()
        self.document_style = DocumentStyles.Normal.value


@dataclass
class MainPageStyle(CorePageStyle):
    """Основной формат страницы"""
    top_margin: Pt | None = Pt(15)
    bottom_margin: Pt | None = Pt(10)
    left_margin: Pt | None = Pt(75)
    right_margin: Pt | None = Pt(75)


@dataclass
class MainParagraphStyle(CoreParagraphStyle):
    """Стиль основного текста"""
    alignment: AlignParagraph | None = AlignParagraph.JUSTIFY.value
    space_after: Pt | None = Pt(0)
    left_indent: Inches | None = Inches(-0.5)
    right_indent: Inches | None = Inches(-0.5)
    line_spacing: float | None = 1.15
    first_line_indent: Pt | None = 20


@dataclass
class HeaderParagraphStyle(CoreParagraphStyle):
    """Стиль для заголовков """
    alignment: AlignParagraph = AlignParagraph.CENTER.value
    left_indent: Inches = Inches(-0.5)
    right_indent: Inches = Inches(-0.5)


class MainDocumentWriter(CoreDocumentWriter):
    def __init__(self):
        super().__init__()


@dataclass
class MainTextStyle(CoreTextStyle):
    """Основной стиль текста"""
    size: Pt = Pt(10)
    name: str = FontNames.TimesNewRoman.value
    bold: bool = False


@dataclass
class HeaderTextStyle(CoreTextStyle):
    size: Pt = Pt(12)
    name: str = FontNames.TimesNewRoman.value
    bold = True
