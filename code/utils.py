import os
import fitz

from config import ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

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

def apply_text_redactions(page, field_placeholder_map):
    for field, placeholder in field_placeholder_map.items():
        if not field:
            continue
        for inst in page.search_for(field):
            page.add_redact_annot(inst, text=placeholder or "[REDACTED]",
                                  fill=(0.75, 0.75, 0.75), text_color=(1, 0, 0), fontsize=8)
    page.apply_redactions()

def remove_images_from_page(page):
    for img in page.get_images(full=True):
        page.delete_image(img[0])

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

def redact_pdf_stream(doc, output_stream, field_placeholder_map, page_ranges_str,
                      remove_images=False, manual_redactions_str=""):
    total_pages = len(doc)
    pages_to_process = parse_page_ranges(page_ranges_str, total_pages)
    for i, page in enumerate(doc):
        if i not in pages_to_process:
            continue
        apply_text_redactions(page, field_placeholder_map)
        apply_manual_redactions(page, manual_redactions_str)
        if remove_images:
            remove_images_from_page(page)
    doc.save(output_stream)
