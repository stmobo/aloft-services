from flask import Flask
app = Flask('aloft_services')

@app.route('/')
def index():
    return "There may possibly be stuff here, at some point."

import aloft_services.pdf_rotate
