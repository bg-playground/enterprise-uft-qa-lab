"""Offline BGSTM External Results v1-shaped export; never sends network requests."""
import argparse
import json
import os
import platform
import re
import sys
import time
import unittest
from pathlib import Path

REQUIREMENTS={'001':['R1'],'002':['R2'],'003':['R3'],'004':['R4'],'005':['R1'],'006':['R4'],'007':['R2'],'008':['R1'],'009':['R1'],'010':['R1'],'011':['R1']}
class Results(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.rows=[]
        self.started={}
        self.failed_subtests={}
    def startTest(self,test):
        self.started[test]=time.monotonic()
        super().startTest(test)
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err:
            self.failed_subtests.setdefault(test,[]).append(self._exc_info_to_string(err,subtest))
    def stopTest(self,test):
        if test in self.failed_subtests and not any(r['external_id']==test.id() for r in self.rows):
            self.record(test,'failed',self.failed_subtests[test][0])
        super().stopTest(test)
    def record(self,test,outcome,error=None):
        match=re.search(r'test_sit_(\d+)',test.id())
        self.rows.append({'external_id':test.id(),'title':test.id(),'outcome':outcome,
            'duration_ms':max(0,round((time.monotonic()-self.started[test])*1000)),
            'error_message':error.splitlines()[-1] if error else None,
            'requirement_external_ids':REQUIREMENTS.get(match.group(1),[]) if match else [],
            'auto_register_requirements':False})
    def addSuccess(self,test):
        super().addSuccess(test)
        self.record(test,'passed')
    def addFailure(self,test,err):
        super().addFailure(test,err)
        self.record(test,'failed',self._exc_info_to_string(err,test))
    def addError(self,test,err):
        super().addError(test,err)
        self.record(test,'failed',self._exc_info_to_string(err,test))
    def addSkip(self,test,reason):
        super().addSkip(test,reason)
        self.record(test,'skipped',reason)
    def addExpectedFailure(self,test,err):
        super().addExpectedFailure(test,err)
        self.record(test,'skipped','Expected failure; not a passing case')
    def addUnexpectedSuccess(self,test):
        super().addUnexpectedSuccess(test)
        self.record(test,'failed','Unexpected success')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',choices=['tests','browser-tests'],required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.discover(args.suite)
    result=unittest.TextTestRunner(verbosity=2,resultclass=Results).run(suite)
    counts={k:sum(r['outcome']==k for r in result.rows) for k in ('passed','failed','skipped')}
    status='passed' if result.wasSuccessful() and result.testsRun>0 and counts['passed']>0 else 'failed'
    payload={'format':'offline BGSTM External Results v1 request templates; not ingested',
      'session':{'runner':'documentflow-unittest@0.1','git_sha':os.getenv('GITHUB_SHA'),
      'git_branch':os.getenv('GITHUB_REF_NAME'),'ci_url':('https://github.com/'+os.environ['GITHUB_REPOSITORY']+'/actions/runs/'+os.environ['GITHUB_RUN_ID']) if os.getenv('GITHUB_REPOSITORY') and os.getenv('GITHUB_RUN_ID') else None,
      'metadata':{'os':platform.platform(),'python':platform.python_version(),'suite':args.suite}},
      'cases':result.rows,'finish':{'status':status,'summary':{'total':len(result.rows),**counts}}}
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    return 0 if status=='passed' else 1
if __name__=='__main__':
    sys.exit(main())
