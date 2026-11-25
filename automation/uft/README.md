# Native UFT preparation — not executed

The VBScript action is an illustrative starting point, not a runnable UFT test package. It requires a licensed Windows host, compatible UFT version/browser, Web add-in, a native IDE-created GUI test and configured object repository. The AOM launcher is also unverified.

## Setup and validation
1. Start the local application with a fresh synthetic database; open http://127.0.0.1:8000 in the supported browser with UFT integration enabled.
2. Create a GUI test, use Object Spy to learn Browser/DocumentFlow, Page/DocumentFlow, WebEdit/Document ID and Title, WebButton/Submit and Process. Confirm logical names and recognition properties in the installed version.
3. Learn a WebElement named Document Row. Bind its identifying property to the current document_id, with a unique row selector (for example XPath //tr[td[1]='INV001'] if the version supports XPath on that test object). This binding is not supplied by the source file and must be configured/verified before execution. Prefer exact cell status verification over the starter substring check when building the final native test.
4. Import test-data/lifecycle.csv into Global DataTable (convert to a supported spreadsheet format if needed), retain headers case_id, document_id, title, expected_status. Set run on all rows. Paste lifecycle.vbs into the action; verify navigation and synchronization in the actual IDE.
5. Run interactively, then validate launch.vbs using the saved test and a new results directory. Capture native result files, UFT version, browser, environment, case IDs and exact repository revision.
6. Repeat the locator lab on a fresh database, compare old and repaired recognition properties, verify unique matching and audit output.

## Boundaries
No native UFT test package, object repository, verified XPath property support, or execution evidence exists yet. Browser/HTTP CI does not establish UFT proficiency. The starter does not independently verify PDF or API integrity. Do not mark native acceptance complete until genuine results are reviewed.
