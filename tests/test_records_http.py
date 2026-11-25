import json
import os
import tempfile
import threading
import unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from unittest.mock import patch
import app

class RecordsHttpSIT(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p=patch.object(app,'DB',os.path.join(tmp.name,'policy.db'))
        p.start()
        self.addCleanup(p.stop)
        server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        t=threading.Thread(target=server.serve_forever,daemon=True)
        t.start()
        self.base='http://127.0.0.1:'+str(server.server_port)
        def stop():
            server.shutdown()
            server.server_close()
            t.join(timeout=5)
        self.addCleanup(stop)
        self.assertEqual(self.call('/api/submit',{'id':'POL001','title':'Invoice'})[0],200)
        self.assertEqual(self.call('/api/process',{'id':'POL001'})[0],200)

    def call(self,path,data=None,role=None):
        headers={'Content-Type':'application/json'}
        if role is not None: headers['X-Lab-Role']=role
        req=Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
        try:
            with urlopen(req,timeout=10) as r: return r.status,r.read()
        except HTTPError as e:
            with e: return e.code,e.read()

    def test_sit_015_role_denials(self):
        data={'id':'POL001','archived_on':'2026-01-01','retention_days':30}
        for role in (None,'viewer','disposition','unknown'):
            self.assertEqual(self.call('/api/policy/classify',data,role)[0],403)
        self.assertEqual(self.call('/api/policy/list',role='viewer')[0],200)
        self.assertEqual(self.call('/api/policy/list')[0],403)
        self.assertEqual(len(json.loads(self.call('/api/audit')[1])),2)

    def test_sit_016_policy_lifecycle(self):
        p='/api/policy/'
        self.assertEqual(self.call(p+'classify',{'id':'POL001','archived_on':'2026-01-01','retention_days':30},'manager')[0],200)
        data={'id':'POL001','today':'2026-01-30'}
        self.assertEqual(self.call(p+'dispose',data,'disposition')[0],409)
        data['today']='2026-01-31'
        self.assertEqual(self.call(p+'hold',{'id':'POL001','enabled':True},'manager')[0],200)
        self.assertEqual(self.call(p+'dispose',data,'disposition')[0],409)
        self.assertEqual(self.call(p+'hold',{'id':'POL001','enabled':False},'disposition')[0],403)
        self.assertEqual(self.call(p+'hold',{'id':'POL001','enabled':False},'manager')[0],200)
        self.assertEqual(self.call(p+'dispose',data,'manager')[0],403)
        self.assertEqual(self.call(p+'dispose',data,'disposition')[0],200)
        self.assertEqual(self.call('/api/pdf/POL001')[0],404)
        self.assertEqual(json.loads(self.call(p+'search?q=invoice',role='viewer')[1]),[])
        self.assertEqual(json.loads(self.call(p+'list',role='viewer')[1])[0]['status'],'disposed')

    def test_sit_017_records_page_and_input(self):
        status,body=self.call('/records')
        self.assertEqual(status,200)
        self.assertIn(b'Synthetic local exercise',body)
        self.assertEqual(self.call('/api/policy/classify',{'id':'POL001','archived_on':'bad','retention_days':30},'manager')[0],400)
        self.assertEqual(self.call('/api/policy/hold',{'id':'POL001','enabled':'true'},'manager')[0],400)
        self.assertEqual(len(json.loads(self.call('/api/audit')[1])),2)
