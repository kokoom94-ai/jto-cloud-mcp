import json
import sqlite3
import time
from pathlib import Path


class State:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS state (kind TEXT, id TEXT, value TEXT, expiry REAL, PRIMARY KEY(kind,id))')

    def connect(self):
        return sqlite3.connect(self.path, timeout=20)

    def put(self, kind, key, value, ttl=86400):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO state VALUES (?,?,?,?)',(kind,key,json.dumps(value,ensure_ascii=False),time.time()+ttl))

    def get(self, kind, key, consume=False):
        with self.connect() as db:
            if consume: db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT value,expiry FROM state WHERE kind=? AND id=?',(kind,key)).fetchone()
            if consume:db.execute('DELETE FROM state WHERE kind=? AND id=?',(kind,key))
            if row and row[1]>time.time():return json.loads(row[0])
        return None

    def delete(self, kind, key):
        with self.connect() as db:db.execute('DELETE FROM state WHERE kind=? AND id=?',(kind,key))

    def purge(self):
        with self.connect() as db:db.execute('DELETE FROM state WHERE expiry<?',(time.time(),))

    def allow(self, key, limit=30, seconds=60):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute("SELECT value,expiry FROM state WHERE kind='limit' AND id=?",(key,)).fetchone()
            n=int(row[0])+1 if row and row[1]>time.time() else 1
            expiry=row[1] if row and row[1]>time.time() else time.time()+seconds
            db.execute("INSERT OR REPLACE INTO state VALUES ('limit',?,?,?)",(key,str(n),expiry))
            return n<=limit
