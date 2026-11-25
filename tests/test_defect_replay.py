"""Controlled defect replay; never change production app or persist a faulty record."""
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
import app

def check_document(c, expected_id, expected_title):
    d=c.execute('SELECT * FROM docs WHERE id=?',(expected_id,)).fetchone()
    assert d['status']=='archived'
    assert d['digest']==hashlib.sha256(d['pdf']).hexdigest()
    reader=PdfReader(io.BytesIO(d['pdf']),strict=True)
    assert reader.metadata.title==expected_title, 'PDF title metadata mismatch'
    assert reader.pages[0].extract_text().splitlines()==['Synthetic document: '+expected_id,expected_title], 'PDF body title mismatch'

class DefectReplay(unittest.TestCase):
    def test_sit_011_wrong_template_field(self):
        from reportlab.pdfgen.canvas import Canvas
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(app,'DB',os.path.join(tmp,'defect.db')):
                c=app.connect()
            try:
                app.submit(c,'DEF001','Invoice')
                original=Canvas.drawString
                def wrong_field(self,x,y,text,*args,**kwargs):
                    if y==690:
                        text='Incorrect template title'
                    return original(self,x,y,text,*args,**kwargs)
                with patch.object(Canvas,'drawString',wrong_field):
                    app.process(c,'DEF001')
                with self.assertRaisesRegex(AssertionError,'PDF body title mismatch'):
                    check_document(c,'DEF001','Invoice')
                # Fresh record, unmodified renderer; same oracle must pass.
                app.submit(c,'DEF002','Invoice')
                app.process(c,'DEF002')
                check_document(c,'DEF002','Invoice')
                out=Path('artifacts/defects')
                out.mkdir(parents=True,exist_ok=True)
                (out/'SIT-011.json').write_text(json.dumps({
                    'case':'SIT-011','classification':'controlled mutation, not observed production defect',
                    'mutated_record':'DEF001','mutation_detected':True,
                    'unmodified_record':'DEF002','control_passed':True,
                    'git_sha':os.environ.get('GITHUB_SHA'),
                    'expected':'Invoice','injected':'Incorrect template title'
                },indent=2),encoding='utf-8')
            finally:
                c.close()

if __name__=='__main__':
    unittest.main()
