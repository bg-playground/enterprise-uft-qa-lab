' UNEXECUTED UFT GUI action source. Paste into a native IDE-created test.
' Configure a shared object repository with the named logical objects below.
' Import lifecycle.csv into Global DataTable, one row per iteration.
Option Explicit
Dim docId, docTitle, expected, caseId, pg, row, statusText
caseId = DataTable.Value("case_id", dtGlobalSheet)
docId = DataTable.Value("document_id", dtGlobalSheet)
docTitle = DataTable.Value("title", dtGlobalSheet)
expected = DataTable.Value("expected_status", dtGlobalSheet)
Set pg = Browser("DocumentFlow").Page("DocumentFlow")
pg.WebEdit("Document ID").Set docId
pg.WebEdit("Title").Set docTitle
pg.WebButton("Submit").Click
Browser("DocumentFlow").Sync
Set row = pg.WebElement("Document Row")
' Configure Document Row as a WebElement with html tag TR and a parameterized
' XPath or equivalent unique description for the document ID. Validate in IDE.
If Not row.Exist(10) Then
    Reporter.ReportEvent micFail, caseId, "Document row missing after submission"
    ExitTestIteration
End If
statusText = row.GetROProperty("innertext")
If InStr(1, statusText, "queued", vbTextCompare) = 0 Then
    Reporter.ReportEvent micFail, caseId, "Expected queued row"
    ExitTestIteration
End If
pg.WebEdit("Document ID").Set docId
pg.WebButton("Process").Click
Browser("DocumentFlow").Sync
If Not row.Exist(10) Then
    Reporter.ReportEvent micFail, caseId, "Document row missing after processing"
    ExitTestIteration
End If
statusText = row.GetROProperty("innertext")
If InStr(1, statusText, expected, vbTextCompare) = 0 Then
    Reporter.ReportEvent micFail, caseId, "Expected " & expected & "; actual " & statusText
Else
    Reporter.ReportEvent micPass, caseId, "Observed expected row state " & expected
End If
