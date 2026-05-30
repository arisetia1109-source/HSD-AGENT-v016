from flask import Flask, render_template, request, jsonify, send_file, session
import os, json, datetime, threading
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hsdagent2025'

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE, 'outputs')
PINS_FILE = os.path.join(BASE, 'pins.json')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

DEFAULT_PINS = {
    'gudang':  {'pin': '1234', 'role': 'gudang',  'label': 'Divisi Gudang'},
    'konten':  {'pin': '2345', 'role': 'konten',  'label': 'Divisi Konten'},
    'live':    {'pin': '3456', 'role': 'live',    'label': 'Divisi Live'},
    'manager': {'pin': '0000', 'role': 'admin',   'label': 'Manager / BOD'},
}

def load_pins():
    if os.path.exists(PINS_FILE):
        with open(PINS_FILE) as f:
            return json.load(f)
    with open(PINS_FILE, 'w') as f:
        json.dump(DEFAULT_PINS, f, indent=2)
    return DEFAULT_PINS

# Progress store
progress_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    pin = data.get('pin', '')
    pins = load_pins()
    for k, v in pins.items():
        if v['pin'] == pin:
            session['role'] = v['role']
            session['label'] = v['label']
            return jsonify({'success': True, 'role': v['role'], 'label': v['label']})
    return jsonify({'success': False})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/pins')
def get_pins():
    pins = load_pins()
    return jsonify(pins)

@app.route('/api/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    slot = request.form.get('slot', 'unknown')
    if not file:
        return jsonify({'success': False, 'error': 'No file'})
    filename = secure_filename(f"{slot}_{file.filename}")
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return jsonify({'success': True, 'path': path, 'name': file.filename})

@app.route('/api/process', methods=['POST'])
def process():
    data = request.json
    slots = data.get('slots', [])  # [{akun, waktu, path}]
    job_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    progress_store[job_id] = {'status': 'running', 'progress': 0, 'log': []}

    def run():
        try:
            from parser import process_pdf
            from excel_writer import write_excel_multi
            all_rows = []
            tf = len(slots)
            for fi, s in enumerate(slots):
                akun, waktu, path = s['akun'], s['waktu'], s['path']
                progress_store[job_id]['log'].append(f'Membaca {akun} {waktu}...')
                def prog(cur, tot, fi=fi, akun=akun, waktu=waktu):
                    pct = int((fi / tf + cur / tot / tf) * 100)
                    progress_store[job_id]['progress'] = pct
                    progress_store[job_id]['log_last'] = f'{akun} {waktu}: hal {cur}/{tot}'
                rows, errs = process_pdf(path, progress_callback=prog)
                for r in rows:
                    r['akun'] = akun
                    r['waktu'] = waktu
                all_rows.extend(rows)
                progress_store[job_id]['log'].append(f'✓ {akun} {waktu}: {len(rows)} baris')

            out = os.path.join(OUTPUT_FOLDER, f'HSD_REKAP_{job_id}.xlsx')
            write_excel_multi(all_rows, out)
            u = len(set(r['no_resi'] for r in all_rows))
            q = sum(r['qty'] for r in all_rows)
            progress_store[job_id].update({
                'status': 'done', 'progress': 100,
                'output': out, 'filename': os.path.basename(out),
                'resi': u, 'qty': q,
                'log': progress_store[job_id]['log'] + [f'SELESAI ✓ — {u} resi · {q} qty']
            })
        except Exception as e:
            progress_store[job_id].update({'status': 'error', 'error': str(e)})

    threading.Thread(target=run, daemon=True).start()
    return jsonify({'job_id': job_id})

@app.route('/api/progress/<job_id>')
def progress(job_id):
    return jsonify(progress_store.get(job_id, {'status': 'unknown'}))

@app.route('/api/download/<job_id>')
def download(job_id):
    info = progress_store.get(job_id, {})
    path = info.get('output')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=info['filename'])
    return 'File not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
