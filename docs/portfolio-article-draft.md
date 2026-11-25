# From SQA Robot to Agentic Testing: What Has Changed — and What Hasn't

*Editorial draft for Brad Guider's review. Not published.*

Software test automation has changed dramatically over the course of my career. I remember building automation with SQA Robot before moving on to tools such as WinRunner. Today, browser automation, APIs, continuous integration and AI-assisted engineering offer possibilities that would have been difficult to imagine in those early years.

But the principles that make automation valuable have remained surprisingly consistent.

## The tools change; the engineering problems remain

Object recognition, synchronization, parameterization and reusable test logic are not new problems. The terminology and implementation details have evolved, but a test still needs to identify the right object, wait for the right state, use meaningful inputs and produce a reliable result.

A fragile test is not made valuable simply by running it faster. A passing result is not useful if the assertion never examines the business outcome. Maintainability is a design decision, not a feature that automatically comes with the latest framework.

## From scripted execution to continuous evidence

Modern automation makes it practical to examine a workflow at several layers. A browser can demonstrate the user journey, an API can expose the underlying transaction, and an independent parser can validate the document that was actually produced.

DocumentFlow QA Lab is a synthetic enterprise testing project designed around that idea. It uses shared test parameters across HTTP and browser tests, verifies generated PDF contents and metadata, and examines records retention and legal holds. A historical CI run recorded 54 passing method executions across four jobs, representing 20 distinct methods. Those numbers are a snapshot, not a claim about every possible workflow.

One investigation arose from a real CI failure: a floating runner image moved to an operating system that the pinned browser tooling did not support. The corrective action was to select a compatible runner without weakening the tests. A second, explicitly controlled exercise substitutes an incorrect document title while preserving a valid checksum. The semantic test detects the discrepancy. These are different kinds of evidence, and both deserve accurate labels.

## Agentic testing is an opportunity, not a shortcut

AI-assisted tools can help develop test ideas, inspect code, investigate failures and organize execution evidence. They can also produce plausible explanations that have not been verified. The distinction matters.

A human-governed workflow should preserve clear requirements, controlled environments, independent assertions and a traceable record of what actually ran. Decisions about acceptable risk, business impact and release readiness should remain accountable to people.

## A consistent quality lifecycle

BGSTM organizes testing into six phases: Test Planning, Test Case Development, Test Environment Preparation, Test Execution, Test Results Analysis and Test Results Reporting. The tools may differ from one team to another, but the lifecycle helps ensure that the evidence supports the decision.

DocumentFlow brings these ideas together. Its portable automation and browser coverage are supported by actual CI evidence. Its native UFT source is preparation for a separate licensed execution milestone, not a claim of completed UFT validation. Its public-facing exercises are simulations, clearly separated from actual test results.

The most interesting part of the evolution from SQA Robot to agentic testing is not that we can automate more. It is that we have an opportunity to make quality evidence more accessible, more repeatable and more useful.

The tools will continue to change. The obligation to ask good questions, understand the business, investigate carefully and report honestly will not.
