from flask import Flask
from main_controller import PDFRedactorController

app = Flask(__name__)
PDFRedactorController(app)

if __name__ == '__main__':
    app.run(debug=True)