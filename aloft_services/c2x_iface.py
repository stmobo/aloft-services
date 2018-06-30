import csv
from io import BytesIO
import zipfile as zf
from aloft_services import app
from flask import request, make_response
from .csv2xml import behaviour_parser as bp
from .csv2xml import csv2xml as c2x

@app.route('/csv2xml', methods=['POST'])
def receive_files():
    lineset = {}
    opponent_meta = None
    for f in request.files:
        reader = csv.DictReader(f)
        partial_lineset, opponent_meta = c2x.csv_to_lineset(reader)

        lineset.update(partial_lineset)

    unique_lines, unique_targeted_lines, num_cases, num_targeted_cases = c2x.get_unique_line_count(lineset)

    opponent_elem = opponent_meta.to_xml()
    meta_elem = opponent_meta.to_meta_xml()

    behaviour_elem, start_elem = c2x.lineset_to_xml(lineset)
    opponent_elem.children.insert(-1, start_elem)
    opponent_elem.children.append(behaviour_elem)

    out_io = BytesIO()

    with zf.ZipFile(out_io) as zip_out:
        with zip_out.open('opponent.xml', 'w') as opponent_out:
            opponent_out.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            opponent_out.write('<!-- '+generate_comment()+' -->\n\n')
            opponent_out.write('<!--\n')
            opponent_out.write('    File Statistics:\n')
            opponent_out.write('    Unique Lines: {}\n'.format(unique_lines))
            opponent_out.write('    Unique Targeted Lines: {}\n'.format(unique_targeted_lines))
            opponent_out.write('    Total Cases: {}\n'.format(num_cases))
            opponent_out.write('    Total Targeted Cases: {}\n'.format(num_targeted_cases))
            opponent_out.write('-->\n\n'.format(num_targeted_cases))
            opponent_out.write(opponent_elem.serialize())

        with zip_out.open('meta.xml', 'w') as meta_out:
            meta_out.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            meta_out.write('<!-- '+generate_comment()+' -->\n')
            meta_out.write(meta_elem.serialize())

    resp = make_response()

    resp.status_code = 200
    resp.headers['Content-Disposition'] = 'attachment; filename="opponent.zip"'
    resp.headers['Content-Type'] = 'application/zip'
    out_io.write(resp.stream)

    out_io.close()

    return resp
