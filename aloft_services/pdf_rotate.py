from aloft_services import app
from werkzeug.exceptions import BadRequest
from flask import request, render_template, make_response
from io import BytesIO
import PyPDF2 as pdf

def rotate_pdf(in_stream, filename, resp, direction, degrees):
    direction = direction.lower()

    if not (direction == 'cw' or direction == 'ccw'):
        raise BadRequest("Direction must be either 'cw' or 'ccw'!")

    if not (degrees % 90 == 0):
        raise BadRequest("Degrees must be a multiple of 90!")

    reader = pdf.PdfFileReader(in_stream)
    writer = pdf.PdfFileWriter()

    for page in reader.pages:
        if direction == 'cw':
            page.rotateClockwise(degrees)
        else:
            page.rotateCounterClockwise(degrees)

        writer.addPage(page)

    resp.status_code = 200
    resp.headers['Content-Disposition'] = "attachment; filename=\"{}\"".format(filename)
    resp.headers['Content-Type'] = 'application/pdf'
    writer.write(resp.stream)

    return resp

@app.route('/pdf/rotate', methods=['POST'])
def interface_form_route():
    direction = request.form.get('direction').lower()
    degrees = int(request.form.get('degrees'), 10)
    filename = request.form.get('filename')
    upload = request.files.get('upload')

    with BytesIO() as bio:
        upload.save(bio)

        return rotate_pdf(
            bio, filename, make_response(), direction, degrees
        )


@app.route('/pdf/rotate/<direction>/<int:degrees>/form', methods=['POST'])
def form_route(direction, degrees):
    filename = request.form.get('filename')
    upload = request.files.get('upload')

    with BytesIO() as bio:
        upload.save(bio)

        return rotate_pdf(
            bio, filename, make_response(), direction, degrees
        )

@app.route('/pdf/rotate/<direction>/<int:degrees>', methods=['POST'])
def direct_upload_route(direction, degrees):
    with BytesIO(request.get_data()) as bio:
        return rotate_pdf(
            bio, 'rotated.pdf', make_response(), direction, degrees
        )
