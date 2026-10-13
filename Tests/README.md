# Tests

Run python Tests/verify_static.py for portable schema/reference checks. These check artifacts and scoring fixtures; they do not execute VB.

In UiPath Studio on Windows, open Tests/RunTests.xaml and Run File on a fresh extracted copy. It invokes Main twice with sample=True and sendEnabled=False, reads Output Excel, checks the five demonstration routes, duplicate counts and top-five ranking. Never point it at a live project State folder. Native Gmail integration tests are manual until your existing project/connection is bound. Data/TestCases.xlsx lists 24 scenarios and expected outcomes.
