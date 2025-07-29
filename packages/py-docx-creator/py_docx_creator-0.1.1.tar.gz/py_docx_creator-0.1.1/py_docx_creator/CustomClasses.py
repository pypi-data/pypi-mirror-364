from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches

from py_docx_creator.CoreClasses import CoreDocumentStyle, DocumentStyles, CorePageStyle, CoreParagraphFormat, CoreTextStyle, \
    FontNames, CoreDocumentWriter


class NormalDocumentStyle(CoreDocumentStyle):
    """Стандартный стиль документа"""
    def __init__(self):
        super().__init__()
        self.document_style = DocumentStyles.Normal.value

class MainPageFormat(CorePageStyle):
    """Основной формат страницы"""
    def __init__(self):
        super().__init__()
        self.top_margin = Pt(15)
        self.bottom_margin = Pt(10)
        self.left_margin = Pt(75)
        self.right_margin = Pt(75)

class MainParagraphFormat(CoreParagraphFormat):
    """Стиль основного текста"""
    def __init__(self):
        super().__init__()
        self.paragraph_alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        self.space_after_paragraph = Pt(0)
        self.paragraph_left_indent = Inches(-0.5)
        self.paragraph_right_indent = Inches(-0.5)
        self.paragraph_line_spacing = 1.15
        self.paragraph_first_line_indent = 20

class HeaderParagraphFormat(CoreParagraphFormat):
    """Стиль для заголовков """
    def __init__(self):
        super().__init__()
        self.paragraph_alignment = WD_ALIGN_PARAGRAPH.CENTER
        self.paragraph_left_indent = Inches(-0.5)
        self.paragraph_right_indent = Inches(-0.5)

class MainTextStyle(CoreTextStyle):
    """Основной стиль текста"""    
    def __init__(self):
        super().__init__()
        self.font_size = Pt(10)
        self.font_name = FontNames.TimesNewRoman.value

class MainDocumentWriter(CoreDocumentWriter):
    def __init__(self):
        super().__init__()