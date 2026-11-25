import functools
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

class PortfolioBrowserSIT(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]/'portfolio'
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(SimpleHTTPRequestHandler,directory=str(root)))
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        def stop():
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        self.addCleanup(stop)
        self.base='http://127.0.0.1:'+str(server.server_port)
        pw=sync_playwright().start()
        self.addCleanup(pw.stop)
        browser=pw.chromium.launch()
        self.addCleanup(browser.close)
        self.page=browser.new_page()
        self.artifacts=Path('artifacts/browser')
        self.artifacts.mkdir(parents=True,exist_ok=True)
        self.page.goto(self.base)
    def test_sit_021_evidence_center(self):
        expect(self.page.locator('#provenance')).to_contain_text('Run #20')
        expect(self.page.locator('#metrics strong').first).to_have_text('54')
        expect(self.page.locator('#jobs tr')).to_have_count(4)
        for width in (390,768,1440):
            self.page.set_viewport_size({'width':width,'height':900})
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))
            self.page.screenshot(path=str(self.artifacts/f'portfolio-{width}.png'),full_page=True)
        self.page.route('**/evidence.json',lambda route:route.abort())
        self.page.reload()
        expect(self.page.locator('#provenance')).to_contain_text('unavailable')
        expect(self.page.locator('#metrics strong')).to_have_count(0)
    def test_sit_022_records_simulation(self):
        p=self.page
        result=p.locator('#record-result')
        p.get_by_role('button',name='Classify',exact=True).click()
        expect(result).to_contain_text('403')
        p.get_by_label('Simulated role').select_option('manager')
        p.get_by_role('button',name='Classify',exact=True).click()
        p.get_by_role('button',name='Set hold').click()
        expect(p.locator('#hold-state')).to_have_text('Active')
        p.get_by_label('Simulated role').select_option('disposition')
        p.get_by_role('button',name='Dispose',exact=True).click()
        expect(result).to_contain_text('409')
        p.get_by_label('Simulated role').select_option('manager')
        p.get_by_role('button',name='Release hold').click()
        p.get_by_label('Simulated role').select_option('disposition')
        p.get_by_label('Simulated disposition date').fill('2026-01-30')
        p.get_by_role('button',name='Dispose',exact=True).click()
        expect(result).to_contain_text('409')
        p.get_by_label('Simulated disposition date').fill('2026-01-31')
        p.get_by_role('button',name='Dispose',exact=True).click()
        expect(p.locator('#state')).to_have_text('Disposed')
        p.get_by_role('button',name='Reset exercise').click()
        expect(p.locator('#state')).to_have_text('Archived')
        expect(p.locator('#audit li')).to_have_count(1)
        p.reload()
        expect(p.locator('#retain')).to_have_text('Not classified')
    def test_sit_023_defect_simulation(self):
        p=self.page
        p.get_by_label('Inject incorrect body title').check()
        p.get_by_role('button',name='Compare document content').click()
        expect(p.locator('#defect-result')).to_contain_text('FAIL')
        p.get_by_label('Inject incorrect body title').uncheck()
        p.get_by_role('button',name='Compare document content').click()
        expect(p.locator('#defect-result')).to_contain_text('PASS')
