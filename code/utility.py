import os
import fitz
import re
from config import ALLOWED_EXTENSIONS

class FileHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def clear_folder(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

class PDFProcessor:
    @staticmethod
    def parse_page_ranges(page_ranges_str, total_pages):
        pages = set()
        if not page_ranges_str.strip():
            return set(range(total_pages))
        parts = page_ranges_str.split(',')
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                pages.update(range(int(start)-1, int(end)))
            else:
                pages.add(int(part)-1)
        return {p for p in pages if 0 <= p < total_pages}

    @staticmethod
    def apply_text_redactions(page, field_placeholder_map):
        for field, placeholder in field_placeholder_map.items():
            if not field:
                continue
            for inst in page.search_for(field):
                page.add_redact_annot(inst, text=placeholder or "[REDACTED]",
                                      fill=(0.75, 0.75, 0.75), text_color=(1, 0, 0), fontsize=8)
        page.apply_redactions()

    @staticmethod
    def apply_regex_text_redactions(page, field_placeholder_map):
        for field, placeholder in field_placeholder_map.items():
            if not field:
                continue
            field = re.compile(field)
            words = page.get_text("words")
            for x0, y0, x1, y1, word, *_ in words:
                if field.search(word):
                    rect = fitz.Rect(x0, y0, x1, y1)
                    page.add_redact_annot(
                        rect,
                        text=placeholder or "[REDACTED]",
                        fill=(0.75, 0.75, 0.75),
                        text_color=(1, 0, 0),
                        fontsize=8
                    )
                
        page.apply_redactions()

    @staticmethod
    def remove_images_from_page(page):
        for img in page.get_images(full=True):
            page.delete_image(img[0])

    @staticmethod
    def apply_manual_redactions(page, manual_redactions_str):
        if not manual_redactions_str.strip():
            return
        boxes = manual_redactions_str.split(';')
        for box in boxes:
            coords = [float(c.strip()) for c in box.split(',')]
            if len(coords) == 4:
                rect = fitz.Rect(*coords)
                page.add_redact_annot(rect, text="[MANUAL REDACTED]",
                                      fill=(0,0,0), text_color=(1,1,1), fontsize=8)
        page.apply_redactions()

    @classmethod
    def redact_pdf_stream(cls, doc, output_stream, field_placeholder_map, page_ranges_str,
                          remove_images=False, manual_redactions_str=""):
        total_pages = len(doc)
        pages_to_process = cls.parse_page_ranges(page_ranges_str, total_pages)
        for i, page in enumerate(doc):
            if i not in pages_to_process:
                continue
            cls.apply_text_redactions(page, field_placeholder_map)
            cls.apply_manual_redactions(page, manual_redactions_str)
            if remove_images:
                cls.remove_images_from_page(page)
        doc.save(output_stream)
