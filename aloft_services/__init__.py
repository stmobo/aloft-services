from flask import Flask, redirect
from logging.config import dictConfig
import os
import os.path as osp

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

if 'ALOFT_SVCS_SETTINGS' in os.environ:
    app.config.from_envvar('ALOFT_SVCS_SETTINGS')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/writing.html')
def writing():
    return app.send_static_file('writing.html')

import aloft_services.pdf_rotate
import aloft_services.pdf_merge
import aloft_services.markdown
import aloft_services.c2x_iface
