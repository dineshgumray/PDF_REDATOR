from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import io
import os
import fitz
import atexit
import config
import utils
from logging_config import setup_logger
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

logger = setup_logger('pdf_redactor_app')

@app.route('/')
def index():
    preview_files = []
    if session.get('show_preview'):
        uploaded_files = os.listdir(config.UPLOAD_FOLDER)
        redacted_files = os.listdir(config.REDACTED_FOLDER)
        for filename in uploaded_files:
            redacted_name = f"redacted_{filename}"
            if redacted_name in redacted_files:
                preview_files.append((filename, redacted_name))
        session['show_preview'] = False
    return render_template('upload.html', preview_files=preview_files)

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        utils.clear_folder(config.UPLOAD_FOLDER)
        utils.clear_folder(config.REDACTED_FOLDER)

        files = request.files.getlist('files[]')
        if not files or not utils.allowed_file(files[0].filename):
            return render_template('upload.html', error_message="No valid files uploaded")

        manual_redactions_input = request.form.get('manual_redactions', '')
        remove_images = request.form.get('remove_images') == 'yes'
        page_ranges_input = request.form.get('page_ranges', '')
        fields = request.form.getlist('fields[]')
        placeholders = request.form.getlist('placeholders[]')
        field_placeholder_map = dict(zip(fields, placeholders))

        for file in files:
            filename = secure_filename(file.filename)
            file_bytes = file.read()
            save_path = os.path.join(config.UPLOAD_FOLDER, filename)
            with open(save_path, "wb") as f_out:
                f_out.write(file_bytes)

            doc = fitz.open(stream=file_bytes, filetype="pdf")
            redacted_stream = io.BytesIO()
            utils.redact_pdf_stream(doc, redacted_stream, field_placeholder_map,
                                    page_ranges_input, remove_images, manual_redactions_input)

            redacted_filename = f"redacted_{filename}"
            with open(os.path.join(config.REDACTED_FOLDER, redacted_filename), "wb") as f_out:
                f_out.write(redacted_stream.getvalue())

        session['show_preview'] = True
        logger.info("Files processed successfully.")
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Error during file processing: {str(e)}")
        return render_template('upload.html', error_message=f"Error: {str(e)}")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER, filename)

@app.route('/redacted/<filename>')
def redacted_file(filename):
    return send_from_directory(config.REDACTED_FOLDER, filename)

@atexit.register
def cleanup_on_exit():
    logger.info("Cleaning up folders on program exit.")
    utils.clear_folder(config.UPLOAD_FOLDER)
    utils.clear_folder(config.REDACTED_FOLDER)

if __name__ == '__main__':
    app.run(debug=True)
