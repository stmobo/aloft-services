from flask import Flask
app = Flask('aloft_services')

@app.route('/')
def index():
    return "There will be stuff here, soon."

import aloft_services.pdf_rotate
