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

    def test_sit_019_records_workflow(self):
        self.page.goto(self.base)
        self.submit('WEB001','Synthetic Invoice')
        self.archive('WEB001', self.page.get_by_role('button',name='Process'))
        self.page.goto(self.base+'/records')
        row=self.page.get_by_role('row').filter(has_text='WEB001')
        expect(row).to_contain_text('archived')
        self.page.get_by_label('Document ID').fill('WEB001')
        status=self.page.get_by_role('status')
        def action(name, code, response):
            with self.page.expect_response(lambda r: '/api/policy/' in r.url and r.request.method=='POST') as pending:
                self.page.get_by_role('button',name=name,exact=True).click()
            self.assertEqual(pending.value.status,code)
            expect(status).to_have_text(response)
        def role(value):
            with self.page.expect_response(lambda r: r.url.endswith('/api/policy/list')) as pending:
                self.page.get_by_label('Simulated role').select_option(value)
            self.assertEqual(pending.value.status,200)
            expect(status).to_have_text('Success')
        action('Classify',403,'403 simulated role denied')
        role('manager')
        action('Classify',200,'Success')
        expect(row).to_contain_text('2026-01-31')
        action('Set hold',200,'Success')
        expect(row.get_by_role('cell').nth(4)).to_have_text('1')
        role('disposition')
        action('Dispose',409,'409 retention or legal hold prevents disposition')
        role('manager')
        action('Release hold',200,'Success')
        expect(row.get_by_role('cell').nth(4)).to_have_text('0')
        role('disposition')
        self.page.get_by_label('Simulated disposition date').fill('2026-01-30')
        action('Dispose',409,'409 retention or legal hold prevents disposition')
        self.page.get_by_label('Simulated disposition date').fill('2026-01-31')
        action('Dispose',200,'Success')
        expect(row).to_contain_text('disposed')
        self.assertEqual(self.page.request.get(self.base+'/api/pdf/WEB001').status,404)
        self.page.get_by_label('Title search').fill('Invoice')
        self.page.get_by_role('button',name='Search archived records').click()
        expect(row).to_have_count(0)
        self.page.get_by_role('button',name='Refresh records').click()
        expect(row).to_contain_text('disposed')
        for width in (390,768,1440):
            self.page.set_viewport_size({'width':width,'height':900})
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))
            self.page.screenshot(path=str(self.artifacts/f'records-{width}.png'),full_page=True)

if __name__ == '__main__':
    unittest.main()
