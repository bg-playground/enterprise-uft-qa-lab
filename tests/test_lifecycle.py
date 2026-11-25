import unittest, sqlite3, tempfile, os, hashlib
from unittest.mock import patch
import app
class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        with patch.object(app,'DB',os.path.join(self.tmp.name,'test.db')): self.c=app.connect()
        self.addCleanup(self.c.close)
    def test_sit_001(self):
        app.submit(self.c,'DOC1','Invoice'); self.assertEqual(app.records(self.c)[0]['status'],'queued')
        app.process(self.c,'DOC1'); d=self.c.execute('select * from docs').fetchone(); self.assertEqual(d['status'],'archived'); self.assertTrue(d['pdf'].startswith(b'%PDF')); self.assertEqual(d['digest'],hashlib.sha256(d['pdf']).hexdigest())
        self.assertEqual([r[0] for r in self.c.execute('select event from audit order by seq')],['submitted','archived'])
    def test_sit_002(self):
        app.submit(self.c,'DOC2','Notice'); app.process(self.c,'DOC2'); app.process(self.c,'DOC2'); self.assertEqual(self.c.execute('select count(*) from audit').fetchone()[0],2)
    def test_sit_003(self):
        app.submit(self.c,'DOC3','Statement'); self.assertRaises(sqlite3.IntegrityError,app.submit,self.c,'DOC3','Other'); self.assertEqual(len(app.records(self.c)),1)
    def test_sit_004(self):
        self.assertRaises(ValueError,app.submit,self.c,'',''); self.assertRaises(KeyError,app.process,self.c,'missing'); self.assertEqual(app.records(self.c),[])
if __name__=='__main__': unittest.main()
