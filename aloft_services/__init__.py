from flask import Flask
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': 'log/app.log',
            'maxBytes': 64 * 1024 * 1024,
            'backupCount': 3,
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})


app = Flask('aloft_services')
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

@app.route('/')
def index():
    return "There may possibly be stuff here, at some point."

import aloft_services.pdf_rotate
