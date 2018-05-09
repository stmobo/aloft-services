from aloft_services import app
from werkzeug.exceptions import BadRequest
from flask import request, render_template, make_response
from io import BytesIO
import PyPDF2 as pdf

def pdf_concat(in_files, filename, resp):
    merger = pdf.PdfFileMerger()

    bios = [BytesIO() for f in in_files]

    for bio, f in zip(bios, in_files):
        f.save(bio)
        merger.append(bio)

    if filename == '' or filename is None:
        filename = 'merged.pdf'

    resp.status_code = 200
    resp.headers['Content-Disposition'] = "attachment; filename=\"{}\"".format(filename)
    resp.headers['Content-Type'] = 'application/pdf'
    merger.write(resp.stream)

    for bio in bios:
        bio.close()

    return resp

@app.route('/pdf/concat', methods=['POST'])
def concat_form_route():
    filename = request.form.get('filename')

    if filename == '' or filename is None:
        filename = upload.filename

    files = [request.files.get(k) for k in sorted(request.files.keys())]

    return pdf_concat(
        files, filename, make_response()
    )
