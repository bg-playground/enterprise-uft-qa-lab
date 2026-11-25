"""Real loopback HTTP integration with isolated database and shared CSV."""
import csv
import io
from pypdf import PdfReader
import hashlib
import json
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch
import app

class HttpSIT(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = patch.object(app, 'DB', os.path.join(self.tmp.name, 'sit.db'))
        p.start()
        self.addCleanup(p.stop)
        self.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, path, data=None, raw=None, kind='application/json'):
        body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
        req = Request(self.base + path, data=body, headers={'Content-Type':kind})
        try:
            with urlopen(req, timeout=10) as response:
                return response.status, response.read()
        except HTTPError as error:
            with error:
                return error.code, error.read()

    def test_sit_005_parameterized_lifecycle(self):
        with (Path(__file__).resolve().parents[1] / 'test-data/lifecycle.csv').open(newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                with self.subTest(case=row['case_id']):
                    id = row['document_id']
                    self.assertEqual(self.request('/api/submit', {'id':id,'title':row['title']})[0],200)
                    self.assertEqual(self.request('/api/pdf/'+id)[0],404)
                    self.assertEqual(self.request('/api/process', {'id':id})[0],200)
                    code, pdf = self.request('/api/pdf/'+id)
                    self.assertEqual(code,200)
                    self.assertTrue(pdf.startswith(b'%PDF'))
                    record = next(r for r in json.loads(self.request('/api/records')[1]) if r['id']==id)
                    self.assertEqual(record['status'],row['expected_status'])
                    self.assertEqual(record['digest'],hashlib.sha256(pdf).hexdigest())
                    self.assertEqual(record['title'],row['title'])

    def test_sit_010_pdf_semantics(self):
        with (Path(__file__).resolve().parents[1] / 'test-data/lifecycle.csv').open(newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                with self.subTest(case=row['case_id']):
                    id, title = row['document_id'], row['title']
                    self.assertEqual(self.request('/api/submit', {'id':id,'title':title})[0],200)
                    self.assertEqual(self.request('/api/process', {'id':id})[0],200)
                    code, pdf = self.request('/api/pdf/'+id)
                    self.assertEqual(code,200)
                    reader = PdfReader(io.BytesIO(pdf), strict=True)
                    self.assertEqual(len(reader.pages),1)
                    self.assertFalse(reader.is_encrypted)
                    self.assertEqual(reader.pages[0].extract_text().splitlines(), ['Synthetic document: '+id, title])
                    self.assertEqual(reader.metadata.title,title)
                    self.assertEqual(reader.metadata.author,'DocumentFlow QA Lab')
                    self.assertEqual(reader.metadata.subject,'Synthetic document '+id)
                    record = next(r for r in json.loads(self.request('/api/records')[1]) if r['id']==id)
                    self.assertEqual(record['digest'],hashlib.sha256(pdf).hexdigest())
                    self.assertEqual(record['title'],title)

    def test_sit_006_invalid_requests(self):
        for raw in (b'{}', b'[]', b'{', b'{"id":"DOC1","title":" "}', b'{"id":4}'):
            with self.subTest(raw=raw):
                self.assertEqual(self.request('/api/submit',raw=raw)[0],400)
        self.assertEqual(self.request('/api/submit',raw=b'{}',kind='text/plain')[0],415)
        self.assertEqual(self.request('/api/process',{'id':'missing'})[0],404)
        self.assertEqual(self.request('/api/unknown',{})[0],404)
        self.assertEqual(json.loads(self.request('/api/records')[1]),[])
        self.assertEqual(json.loads(self.request('/api/audit')[1]),[])

    def test_sit_007_concurrent_retries(self):
        self.assertEqual(self.request('/api/submit',{'id':'RACE1','title':'Retry'})[0],200)
        barrier = threading.Barrier(4)
        def retry(_):
            barrier.wait(timeout=5)
            return self.request('/api/process',{'id':'RACE1'})[0]
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(list(pool.map(retry,range(4))),[200]*4)
        events = json.loads(self.request('/api/audit')[1])
        self.assertEqual([e['event'] for e in events],['submitted','archived'])
        self.assertEqual(len(json.loads(self.request('/api/records')[1])),1)

if __name__ == '__main__':
    unittest.main()
