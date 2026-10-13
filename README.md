# ResolveX — Multi-Organization Complaint Automation

**Built:** reusable VB.NET UiPath complaint core, sample intake, keyword scoring, optional approved AI gateway call, priority/sentiment, Excel routing, FAQ recommendations, deterministic tickets, draft previews, duplicate protection, per-complaint exception handling and top-five report.

**Needs your existing project to finish:** native Google Workspace Gmail read/send adapter binding. Your local ResolveX_Automation/project.json, Main.xaml and ClassifyComplaint.xaml were not available in this environment. Installed Google Workspace version and connection metadata could not be inspected. No connection was copied, recreated or overwritten. ReadGmail accepts the installed Get Email List output. SendGmail deliberately fails closed until a native activity is added with your existing connection. This ZIP is not a finished live Gmail deployment.

**GitHub upload:** rejected with 403 Resource not accessible by integration, despite repository owner push permission. Reconnect the GitHub app with ResolveX selected and Contents read/write. No remote files were created or changed.

## Start the local sample prototype
1. Extract the ZIP. Keep the whole ResolveX_Hackathon folder together.
2. In Windows UiPath Studio Desktop 2024.10 or newer, open project.json. Restore UiPath.System.Activities 24.10.7. Use Windows compatibility and Visual Basic expressions.
3. Run Validate Project. Set Main arguments: in_ProjectRoot = the absolute extracted folder, in_UseSample=True, in_SendEnabled=False, in_AIEnabled=False, in_AIApproved=False. Leave in_GmailEmails empty. Running standalone with no input also selects sample mode.
4. Run Main.xaml. Review Output/Complaints_Log.xlsx, Output/Priority_Report.xlsx and Output/Drafts/*.json. Initial routing addresses are blank and Active=False, so sample rows show RouteUnconfigured; unknown/ambiguous cases show ManualReview.
5. Run Tests/RunTests.xaml in a separate fresh extracted copy. It checks five main scenarios, duplicate intake and priority ranking. No real email is involved.

## Use the working Gmail connection
Follow [Gmail integration](Docs/GMAIL_SETUP.md). Back up your current project first. Import under a separate subfolder; do not replace your original Main.xaml or ClassifyComplaint.xaml. The controller uses absolute workflow paths derived from in_ProjectRoot, so its files can stay in that subfolder. Use an Invoke Workflow File from your existing Main to this new Main and pass Get Email List's output. Select your existing Gmail connection on native activities.

## Included workbooks
Data/Routing.xlsx: 56 organization/category rows for Flipkart, Amazon, Samsung, Airtel, Jio, Swiggy, Zomato and Meesho. Blank recipients and inactive routes are intentional. Data/FAQ_KnowledgeBase.xlsx: 56 editable demonstration FAQ entries; these are prototype templates, not official company policies. Data/Complaints_Log.xlsx and Data/Priority_Report.xlsx are empty templates, populated under Output on execution. Data/TestCases.xlsx has 24 functional and error scenarios.

Required complaint columns are present; ClassificationSource, Summary and EscalationRequired are additional audit fields. Receipt timestamps are UTC ISO8601 strings for unambiguous cross-system exchange. Priority sorting parses timestamps, rather than lexically comparing display text. XLSX files use text cells at runtime to prevent formula injection from email content.

## Control points
No real recipient address is invented. Configure Data/Routing.xlsx AND Config/AuthorizedRecipients.json with company-scoped approved test inboxes. Active=True alone is insufficient. Config/ManualReviewRecipients.json may specify a separately approved inbox per organization, including Unknown; it must also be in AuthorizedRecipients.json. Otherwise manual review remains local.

SendEnabled=False is the default. Sample mode cannot send. Exact owner-reviewed recipient/subject/body/organization/action ID and a future expiry are required in Config/SendApproval.json. Native sender binding is additionally required. Never commit local approval, logs, customer messages or sender binding flags.

FAQ output is a recommendation included in the department notification; it is not automatically sent to the customer. AI cannot set a recipient. Unsupported/ambiguous companies remain manual review independently of AI.

## Architecture and verification
The ten requested workflows and six helpers are in Workflows plus Main.xaml. Full argument contracts, variable types, expressions and activity configuration are in Docs/WORKFLOWS.md. Code uses Invoke Code in UiPath with .NET APIs; no external PowerShell/Python service is required for normal operation. XLSX read/write helpers use OpenXML ZIP data and need no installed Microsoft Excel. Google Workspace package is required only for your native connection adapters and must retain your installed version.

[Validation](Docs/VALIDATION.md) documents completed static checks and runtime checks still outstanding. XML parsing does not prove UiPath compilation. Neither UiPath Studio nor a Windows/.NET runtime was available here. No real Gmail reads, drafts or sends were executed. [Hackathon demo](Docs/DEMO.md) gives a reproducible sequence.

Run only one controller per project folder. A file lock enforces this in Main. Use separate copies for independent organizations if sharing the workstation. Local allowlists are a prototype control, not enterprise role-based access control.

## Upload alternative
Tools/Upload-ToGitHub.ps1 can be run on your computer with Git, GitHub CLI and an authenticated account. It inspects write access, preserves existing files, validates the clean demo payload and uploads to main only if the repository is empty; otherwise it creates a separate branch and draft PR. It requires Python for upload preflight only. It was not executed here. Reconnecting the ChatGPT GitHub integration is the preferred way for me to complete the upload.
