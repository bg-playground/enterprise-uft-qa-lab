"""Synthetic records policy; service layer only, no user authentication claims."""
from datetime import date, timedelta

def install(c):
    c.execute("""CREATE TABLE IF NOT EXISTS record_policy(
        id TEXT PRIMARY KEY REFERENCES docs(id), retain_until TEXT NOT NULL,
        legal_hold INTEGER NOT NULL DEFAULT 0, disposed INTEGER NOT NULL DEFAULT 0)""")

def classify(c, doc_id, archived_on, retention_days):
    if type(retention_days) is not int or not 1 <= retention_days <= 3650:
        raise ValueError('retention must be 1–3650 days')
    if type(archived_on) is not date:
        raise ValueError('date required')
    with c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT status FROM docs WHERE id=?',(doc_id,)).fetchone()
        if not row or row['status']!='archived': raise ValueError('archived record required')
        c.execute('INSERT INTO record_policy(id,retain_until) VALUES(?,?)',
                  (doc_id,(archived_on+timedelta(days=retention_days)).isoformat()))
        c.execute('INSERT INTO audit(id,event) VALUES(?,?)',(doc_id,'classified'))

def hold(c, doc_id, enabled):
    if type(enabled) is not bool: raise ValueError('boolean required')
    with c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT legal_hold,disposed FROM record_policy WHERE id=?',(doc_id,)).fetchone()
        if not row or row['disposed']: raise ValueError('active classified record required')
        if row['legal_hold']==int(enabled): return
        c.execute('UPDATE record_policy SET legal_hold=? WHERE id=?',(int(enabled),doc_id))
        c.execute('INSERT INTO audit(id,event) VALUES(?,?)',(doc_id,'hold_set' if enabled else 'hold_released'))

def dispose(c, doc_id, today):
    if type(today) is not date: raise ValueError('date required')
    with c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT * FROM record_policy WHERE id=?',(doc_id,)).fetchone()
        if not row: raise ValueError('classification required')
        if row['disposed']: return False
        if row['legal_hold'] or today < date.fromisoformat(row['retain_until']):
            raise PermissionError('retention or hold prevents disposal')
        c.execute("UPDATE docs SET status='disposed',pdf=NULL,digest=NULL WHERE id=?",(doc_id,))
        c.execute('UPDATE record_policy SET disposed=1 WHERE id=?',(doc_id,))
        c.execute('INSERT INTO audit(id,event) VALUES(?,?)',(doc_id,'disposed'))
        return True

def search(c, query):
    return [dict(r) for r in c.execute("""SELECT id,title,status FROM docs
        WHERE status='archived' AND instr(lower(title),lower(?))>0 ORDER BY id""",(query,))]
