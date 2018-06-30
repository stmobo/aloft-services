import csv
from io import BytesIO, StringIO
import zipfile as zf
from aloft_services import app
from flask import request, send_file
from .csv2xml import behaviour_parser as bp
from .csv2xml import csv2xml as c2x
import logging

c2x.config_opponents_dir('/home/stmobo/spnati.gitlab.io/opponents')

@app.route('/csv2xml', methods=['POST'])
def receive_files():
    lineset = {}
    opponent_meta = None
    
    logging.info("Processing request data...")
    with BytesIO(request.get_data()) as bio:
        for key, file in request.files.items(multi=True):
            logging.info("Processing file: {}".format(file.filename))
            file.save(bio)
            
        logging.info("Read {} bytes total.".format(len(bio.getvalue())))
        all_data = bio.getvalue().decode('utf-8')
        
        with StringIO(all_data) as sio:
            reader = csv.DictReader(sio)
            lineset, opponent_meta = c2x.csv_to_lineset(reader)
            
    unique_lines, unique_targeted_lines, num_cases, num_targeted_cases = c2x.get_unique_line_count(lineset)

    opponent_elem = opponent_meta.to_xml()
    meta_elem = opponent_meta.to_meta_xml()

    behaviour_elem, start_elem = c2x.lineset_to_xml(lineset)
    opponent_elem.children.insert(-1, start_elem)
    opponent_elem.children.append(behaviour_elem)

    out_io = BytesIO()

    with zf.ZipFile(out_io, 'w', zf.ZIP_DEFLATED) as zip_out:
        with zip_out.open('opponent.xml', 'w') as opponent_out:
            data_str  = "<?xml version='1.0' encoding='UTF-8'?>\n"
            data_str += '<!-- '+c2x.generate_comment()+' -->\n\n'
            data_str += '<!--\n'
            data_str += '    File Statistics:\n'
            data_str += '    Unique Lines: {}\n'.format(unique_lines)
            data_str += '    Unique Targeted Lines: {}\n'.format(unique_targeted_lines)
            data_str += '    Total Cases: {}\n'.format(num_cases)
            data_str += '    Total Targeted Cases: {}\n'.format(num_targeted_cases)
            data_str += '-->\n\n'.format(num_targeted_cases)
            data_str += opponent_elem.serialize()
            
            opponent_out.write(data_str.encode('utf-8'))

        with zip_out.open('meta.xml', 'w') as meta_out:
            data_str  = "<?xml version='1.0' encoding='UTF-8'?>\n"
            data_str += '<!-- '+c2x.generate_comment()+' -->\n'
            data_str += meta_elem.serialize()
            
            meta_out.write(data_str.encode('utf-8'))
            
    out_io.seek(0)
    
    return send_file(out_io, as_attachment=True, attachment_filename='opponent.zip')
