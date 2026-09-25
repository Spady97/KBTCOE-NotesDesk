from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os, uuid, base64, hashlib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, 'database', 'notesdesk.db')
UPLOAD_DIR = os.path.join(ROOT, 'uploads')
FRONTEND_DIR = os.path.join(ROOT, 'frontend')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    con.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        branch TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        avatar TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_phone TEXT NOT NULL,
        title TEXT NOT NULL,
        branch TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        file_name TEXT NOT NULL,
        listing_type TEXT NOT NULL,
        doc_ext TEXT,
        price REAL NOT NULL DEFAULT 0,
        upi TEXT,
        sample_img1 TEXT,
        sample_img2 TEXT,
        file_path TEXT,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        item_id INTEGER,
        item_title TEXT,
        buyer_phone TEXT,
        buyer_name TEXT,
        total_amount REAL,
        seller_payout REAL,
        status TEXT,
        time TEXT
    );
    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'OPEN',
        created_at TEXT NOT NULL
    );
    ''')
    con.commit(); con.close()


def pw_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def row_user(r):
    return {'id': r['id'], 'name': r['name'], 'branch': r['branch'], 'phone': r['phone'], 'avatar': r['avatar'] or ''}


def row_material(r):
    return {
        'id': r['id'], 'sellerPhone': r['seller_phone'], 'title': r['title'],
        'branch': r['branch'], 'subject': r['subject'], 'topic': r['topic'],
        'fileName': r['file_name'], 'listingType': r['listing_type'],
        'docExt': r['doc_ext'] or '', 'price': r['price'], 'upi': r['upi'] or '',
        'samplePages': [
            {'label':'Sample 1','img':r['sample_img1'] or ''},
            {'label':'Sample 2','img':r['sample_img2'] or ''}
        ],
        'fileUrl': ('/files/' + os.path.basename(r['file_path'])) if r['file_path'] else ''
    }


@app.route('/')
def home():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    full = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json(silent=True) or {}
    action = data.get('action')
    con = db()
    try:
        if action == 'register_user':
            name = str(data.get('name','')).strip(); phone = str(data.get('phone','')).strip()
            branch = str(data.get('branch','')).strip(); password = str(data.get('password',''))
            if not name or not phone or not branch or not password:
                return jsonify(success=False, message='All fields are required.')
            if con.execute('SELECT 1 FROM users WHERE phone=?',(phone,)).fetchone():
                return jsonify(success=False, message='Phone number already exists.')
            con.execute('INSERT INTO users(name,branch,phone,password_hash,created_at) VALUES(?,?,?,?,?)',
                        (name,branch,phone,pw_hash(password),datetime.now().isoformat()))
            con.commit()
            r=con.execute('SELECT * FROM users WHERE phone=?',(phone,)).fetchone()
            return jsonify(success=True,user=row_user(r))

        if action == 'login_user':
            phone=str(data.get('phone','')).strip(); password=str(data.get('password',''))
            r=con.execute('SELECT * FROM users WHERE phone=? AND password_hash=?',(phone,pw_hash(password))).fetchone()
            if not r: return jsonify(success=False,message='Invalid WhatsApp Phone Number or Password.')
            purchases=[dict(x) for x in con.execute('SELECT * FROM orders WHERE buyer_phone=? ORDER BY time DESC',(phone,)).fetchall()]
            return jsonify(success=True,user=row_user(r),purchases=purchases)

        if action == 'get_all_materials':
            rows=con.execute('SELECT * FROM materials ORDER BY id DESC').fetchall()
            return jsonify(success=True,materials=[row_material(r) for r in rows])

        if action == 'publish_material':
            seller=str(data.get('sellerPhone','')).strip()
            title=str(data.get('title','')).strip(); branch=str(data.get('branch','')).strip()
            subject=str(data.get('subject','')).strip(); topic=str(data.get('topic','')).strip()
            file_name=str(data.get('fileName','study_file')).strip(); listing=str(data.get('listingType','soft_only'))
            ext=str(data.get('docExt','pdf')); price=float(data.get('price') or 0); upi=str(data.get('sellerUPI',''))
            sample1=data.get('sampleImg1',''); sample2=data.get('sampleImg2','')
            file_path=None
            b64=data.get('base64Data')
            if b64:
                try:
                    raw=base64.b64decode(b64)
                    safe=f'{uuid.uuid4().hex}_{os.path.basename(file_name)}'
                    file_path=os.path.join(UPLOAD_DIR,safe)
                    with open(file_path,'wb') as f: f.write(raw)
                except Exception:
                    file_path=None
            cur=con.execute('''INSERT INTO materials(seller_phone,title,branch,subject,topic,file_name,listing_type,doc_ext,price,upi,sample_img1,sample_img2,file_path,created_at)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                            (seller,title,branch,subject,topic,file_name,listing,ext,price,upi, sample1,sample2,file_path,datetime.now().isoformat()))
            con.commit()
            r=con.execute('SELECT * FROM materials WHERE id=?',(cur.lastrowid,)).fetchone()
            return jsonify(success=True,material=row_material(r))

        if action == 'create_cashfree_order':
            # Demo/local payment flow. Real Cashfree credentials are required for live payments.
            item_title=str(data.get('itemTitle','Study Material'))
            total=float(data.get('totalAmount') or 0); seller=float(data.get('sellerShare') or 0)
            buyer=str(data.get('buyerPhone','')); name=str(data.get('buyerName',''))
            order_id='LOCAL-'+uuid.uuid4().hex[:12].upper()
            con.execute('INSERT INTO orders(order_id,item_id,item_title,buyer_phone,buyer_name,total_amount,seller_payout,status,time) VALUES(?,?,?,?,?,?,?,?,?)',
                        (order_id,data.get('itemId'),item_title,buyer,name,total,seller,'PAID (LOCAL DEMO)',datetime.now().isoformat()))
            con.commit()
            # The frontend expects a paymentSessionId. In this local version it is only a demo token.
            return jsonify(success=True,paymentSessionId=order_id,orderId=order_id,demo=True)

        return jsonify(success=False,message='Unknown action.')
    finally:
        con.close()


@app.route('/api/support', methods=['POST'])
def support():
    d=request.get_json(silent=True) or {}
    con=db(); con.execute('INSERT INTO support_messages(name,phone,subject,message,created_at) VALUES(?,?,?,?,?)',
                         (d.get('name',''),d.get('phone',''),d.get('subject',''),d.get('message',''),datetime.now().isoformat()))
    con.commit(); con.close()
    return jsonify(success=True,message='Support message submitted.')

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
