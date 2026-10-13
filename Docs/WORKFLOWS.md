# Workflow arguments and activity configuration

All core activities are standard UiPath System activities: Sequence, Invoke Code (Language=VBNet), Invoke Workflow File, For Each, If and Try Catch. No native Gmail connection metadata was available; its exact configuration is in GMAIL_SETUP.md.

Record = Dictionary(Of String, String). Records = List(Of Dictionary(Of String, String)). DataTable = System.Data.DataTable. io_Complaint uses In direction because a mutable dictionary reference is updated in place; no replacement object is returned.

## LoadWorkbook

| Argument | Direction | .NET type |
|---|---|---|
| in_Path | In | String |
| out_Table | Out | System.Data.DataTable |

## SaveWorkbook

| Argument | Direction | .NET type |
|---|---|---|
| in_Path | In | String |
| in_Table | In | System.Data.DataTable |

## ReadGmail

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| in_UseSample | In | Boolean |
| in_GmailEmails | In | Object |
| out_Emails | Out | List(Of Dictionary(Of String, String)) |

## ClassifyComplaint

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| io_Complaint | In | Dictionary(Of String, String) |
| in_AIEnabled | In | Boolean |
| in_AIApproved | In | Boolean |

## DeterminePriority

| Argument | Direction | .NET type |
|---|---|---|
| io_Complaint | In | Dictionary(Of String, String) |

## FindDepartment

| Argument | Direction | .NET type |
|---|---|---|
| io_Complaint | In | Dictionary(Of String, String) |
| in_Routing | In | System.Data.DataTable |
| in_AuthorizedRecipients | In | List(Of Dictionary(Of String, String)) |

## GenerateResponse

| Argument | Direction | .NET type |
|---|---|---|
| io_Complaint | In | Dictionary(Of String, String) |
| in_FAQ | In | System.Data.DataTable |

## RouteComplaint

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| io_Complaint | In | Dictionary(Of String, String) |
| out_Actions | Out | List(Of Dictionary(Of String, String)) |

## HandleExceptions

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| io_Complaint | In | Dictionary(Of String, String) |
| in_Error | In | System.Exception |

## LogComplaint

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| io_Complaint | In | Dictionary(Of String, String) |
| in_Log | InOut | System.Data.DataTable |

## GeneratePriorityReport

| Argument | Direction | .NET type |
|---|---|---|
| in_Log | In | System.Data.DataTable |
| out_Report | Out | System.Data.DataTable |

## SendGmail

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| in_Action | In | Dictionary(Of String, String) |
| in_SendEnabled | In | Boolean |
| out_SendStatus | Out | String |

## ApproveAction

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| in_Action | In | Dictionary(Of String, String) |
| in_SendEnabled | In | Boolean |
| out_Approved | Out | Boolean |

## TrackDispatch

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| in_Action | In | Dictionary(Of String, String) |
| in_Status | In | String |
| out_Skip | Out | Boolean |

## DispatchActions

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| io_Complaint | In | Dictionary(Of String, String) |
| in_Actions | In | List(Of Dictionary(Of String, String)) |
| in_SendEnabled | In | Boolean |

## Main

| Argument | Direction | .NET type |
|---|---|---|
| in_ProjectRoot | In | String |
| in_UseSample | In | Boolean |
| in_GmailEmails | In | Object |
| in_SendEnabled | In | Boolean |
| in_AIEnabled | In | Boolean |
| in_AIApproved | In | Boolean |

## Main variables

| Variable | Type | Purpose |
|---|---|---|
| effectiveRoot | String | Extracted/imported project root |
| sampleMode | Boolean | Sample if selected or standalone no Gmail input |
| emails, actions, authorized | Records | Intake, notifications, approved organization recipients |
| routes, faq, log, report | DataTable | Excel sources and output tables |
| skip | Boolean | Already audited ID in this run mode |
| lockHandle | Object (FileStream) | Exclusive run lock released in Finally |

For Each item complaint is a Record. caughtException is System.Exception. DispatchActions variables approved/skip are Boolean and sendStatus is String. Loop item action is Record.

## Useful expressions

- Batch intake argument: in_GmailEmails = gmailEmails (Get Email List output).
- Department recipient: New String(){in_Action("To")}.
- Native send subject/body: in_Action("Subject") / in_Action("Body").
- Send gate: in_SendEnabled.
- Successful native send: out_SendStatus = "Sent" (only after activity success).
- Unique ticket: RX- plus first 16 hex SHA256 characters of Gmail message ID.
- AI and rules source: complaint("ClassificationSource").

## Scoring and precedence

Matches are case-insensitive and use word boundaries. Common suffixes s/ed/ing are accepted for single-word keywords; explicit multiword phrases carry weight 4. Generic order, package and not working carry weight 1; other single keywords carry weight 3. Each configured keyword contributes once even if repeated. Related phrase matches may also add to the same category score. Category tie is resolved to a deterministic label for display and ManualReview for routing. Unsupported/multiple company mentions always require manual review.

Main order: validate/lock, load routing/FAQ/log, recover durable audit, ReadGmail, For Each -> duplicate check -> ClassifyComplaint -> DeterminePriority -> FindDepartment -> GenerateResponse -> RouteComplaint -> LogComplaint+SaveWorkbook -> DispatchActions -> LogComplaint+SaveWorkbook. Per-message catch -> HandleExceptions -> LogComplaint. Final GeneratePriorityReport and SaveWorkbook.

## Dependencies

Standalone core: UiPath.System.Activities [24.10.7], Windows VB project, Studio 2024.10+. Standard .NET assemblies are declared in each XAML TextExpression references. Core Excel ZIP helpers use System.IO.Compression / System.Xml.Linq instead of Excel activities. Existing Gmail integration: retain your installed UiPath.GSuite.Activities package/version and connection. Do not overwrite your project.json with this standalone project.json when importing into your current project.
