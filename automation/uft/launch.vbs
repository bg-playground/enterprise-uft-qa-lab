' UNVERIFIED starter: requires licensed UFT, interactive Windows session,
' and a native test created/saved in the IDE. No native test is bundled.
Option Explicit
Dim qt, testPath, resultsPath, options
If WScript.Arguments.Count <> 2 Then WScript.Quit 2
testPath = WScript.Arguments(0)
resultsPath = WScript.Arguments(1)
Set qt = CreateObject("QuickTest.Application")
If Not qt.Launched Then qt.Launch
qt.Visible = True
qt.Open testPath, True
Set options = CreateObject("QuickTest.RunResultsOptions")
options.ResultsLocation = resultsPath
qt.Test.Run options, True
WScript.Echo qt.Test.LastRunResults.Status
If LCase(qt.Test.LastRunResults.Status) = "passed" Then WScript.Quit 0
WScript.Quit 1
