"""Independent browser engine, using the same CSV as HTTP SIT."""
import csv
import hashlib
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from playwright.sync_api import sync_playwright, expect
import app

class BrowserSIT(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        p = patch.object(app, 'DB', os.path.join(temp.name, 'browser.db'))
        p.start()
        self.addCleanup(p.stop)
        server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def stop():
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        self.addCleanup(stop)
        self.base = 'http://127.0.0.1:' + str(server.server_port)
        pw = sync_playwright().start()
        self.addCleanup(pw.stop)
        browser = pw.chromium.launch()
        self.addCleanup(browser.close)
        context = browser.new_context()
        self.addCleanup(context.close)
        self.page = context.new_page()
        self.artifacts = Path('artifacts/browser')
        self.artifacts.mkdir(parents=True, exist_ok=True)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.addCleanup(lambda: context.tracing.stop(path=str(self.artifacts / (self._testMethodName + '.zip'))))

    def submit(self, id, title):
        self.page.get_by_label('Document ID').fill(id)
        self.page.get_by_label('Title').fill(title)
        self.page.get_by_role('button',name='Submit').click()
        expect(self.page.get_by_role('row').filter(has_text=id)).to_contain_text('queued')

    def archive(self, id, locator):
        self.page.get_by_label('Document ID').fill(id)
        locator.click()
        expect(self.page.get_by_role('row').filter(has_text=id)).to_contain_text('archived')

    def test_sit_008_browser_csv(self):
        with (Path(__file__).resolve().parents[1] / 'test-data/lifecycle.csv').open(newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                with self.subTest(case=row['case_id']):
                    self.page.goto(self.base)
                    self.submit(row['document_id'], row['title'])
                    self.archive(row['document_id'], self.page.get_by_role('button',name='Process'))
                    res = self.page.request.get(self.base+'/api/records')
                    self.assertEqual(res.status,200)
                    record = next(x for x in res.json() if x['id']==row['document_id'])
                    pdf = self.page.request.get(self.base+'/api/pdf/'+row['document_id'])
                    self.assertEqual(pdf.status,200)
                    self.assertEqual(record['digest'],hashlib.sha256(pdf.body()).hexdigest())
                    self.assertEqual(record['status'],row['expected_status'])
                    self.assertEqual(record['title'],row['title'])

    def test_sit_009_xpath_drift(self):
        self.page.goto(self.base)
        expect(self.page.locator("xpath=//button[@id='process']")).to_have_count(1)
        self.page.goto(self.base+'/locator-lab')
        self.submit('XPATH1','Locator drift')
        legacy = self.page.locator("xpath=//button[@id='process']")
        expect(legacy).to_have_count(0)
        repaired = self.page.locator("xpath=//button[@data-testid='archive-document']")
        expect(repaired).to_have_count(1)
        self.page.screenshot(path=str(self.artifacts/'locator-drift.png'))
        self.archive('XPATH1', repaired)
        events = self.page.request.get(self.base+'/api/audit').json()
        self.assertEqual([e['event'] for e in events],['submitted','archived'])

if __name__ == '__main__':
    unittest.main()
