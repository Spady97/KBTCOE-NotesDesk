CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  branch TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  avatar TEXT DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE TABLE materials (
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

CREATE TABLE orders (
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

CREATE TABLE support_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  phone TEXT,
  subject TEXT,
  message TEXT,
  status TEXT DEFAULT 'OPEN',
  created_at TEXT NOT NULL
);
