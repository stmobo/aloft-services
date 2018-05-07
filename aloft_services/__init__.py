from flask import Flask
app = Flask('aloft_services')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

@app.route('/')
def index():
    return "There may possibly be stuff here, at some point."

import aloft_services.pdf_rotate
