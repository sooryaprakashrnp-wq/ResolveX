# Preserve the existing Gmail connection

## What is missing for exact integration
The actual ResolveX_Automation project was not supplied. Inspect Project > Dependencies or open its project.json to find the exact UiPath.GSuite.Activities version. Keep that version. Modern connection-based activities and their connection metadata vary across versions; exporting your real XAML is required to serialize an exact reusable read/send adapter. Send the project ZIP without .local, .objects, tokens, credentials or customer messages to finish that binding.

Do not delete your existing Get Newest Email or configured connection until the batch reader is validated. Make a backup copy of the project, then keep the downloaded ResolveX_Hackathon folder as a subfolder. Invoke the downloaded Main with in_ProjectRoot pointing to that subfolder. All internal workflow file paths are absolute from that root.

## Batch reader — native Google Workspace activity
In the existing project Main, before invoking the new controller:
1. Add **Get Email List** (Google Workspace / Gmail). If unavailable in your installed package, use **For Each Email** and collect its CurrentEmail objects into a List using Add To Collection. Get Newest Email returns one email; it cannot by itself provide batch intake.
2. DisplayName: Read complaint emails from authorized ResolveX inbox.
3. Gmail connection: select the same working connection already used by Get Newest Email.
4. Email folder or label: Inbox. Use the picker, or Folder path input mode = "INBOX" if supported.
5. Limit emails to first: 50. Include subfolders=False, Unread only=False, Mark as read=False, With attachments only=False. Additional filters: empty for initial demo; constrain From/Subject for safe test intake afterwards.
6. Output Emails: create variable gmailEmails using the activity's automatic output type List(Of GmailMessage). Keep the package-resolved type; do not replace with System.Net.Mail.MailMessage.
7. Add Invoke Workflow File for the downloaded controller Main.xaml. Import arguments and set:
   - in_ProjectRoot: absolute downloaded subfolder string
   - in_UseSample: False
   - in_GmailEmails: gmailEmails
   - in_SendEnabled: False
   - in_AIEnabled: False
   - in_AIApproved: False
8. Keep Mark as read disabled. Local audit/journal records prevent duplicate handling. Do not label or mark messages processed until the controller succeeds.

ReadGmail.xaml accepts the collection as Object to preserve compatibility with the package-resolved GmailMessage assembly. It reads the documented properties MessageId, FromAddress/SenderAddress, Subject, Body and ReceivedDateTime. Missing IDs or timestamps require manual review. HTML-only bodies are not stripped or automatically interpreted; check body extraction with your installed package. Attachments are not included in the department notification.

Add Retry Scope around the native **read** activity if needed: maximum 3 total attempts (initial plus 2 retries), retry interval 5 seconds. Reauthorization/permission errors require user action rather than repeated retries. Do not log exception.Message or server responses containing private data. An intake authentication error occurs before the new controller; it cannot be logged per complaint because no complaint list was returned.

## Native Gmail sender adapter
Open downloaded Workflows/SendGmail.xaml in the existing UiPath project. It currently contains a fail-closed Invoke Code, not a serialized Gmail activity. Replace ONLY that adapter body after preserving your original project:

1. Add an If activity: condition **in_SendEnabled**.
2. In Then add **Send Email** (Google Workspace / Gmail).
3. Gmail connection: same authorized existing connection.
4. To: **New String(){in_Action("To")}**.
5. Subject: **in_Action("Subject")**.
6. Body: **in_Action("Body")** (plain text). CC/BCC/attachments empty.
7. Save as draft: **False** for the approved send path.
8. After Send Email completes successfully, Assign **out_SendStatus = "Sent"**. On error, allow the exception to propagate to DispatchActions; do not report Sent from Finally or a catch block.
9. Else Assign **out_SendStatus = "DryRun"**. This branch must have no send activity.
10. After Studio Validate and a dry-run inspection, create an empty Config/SenderBound.flag file. The flag only records that the adapter has been bound; it is not owner send approval.

For an optional real Gmail draft preview, make a separate manual workflow using the same Send Email activity with **Save as draft=True** and the same To/Subject/Body expressions. Creating mailbox drafts changes Gmail, so do this only intentionally with approved test recipients. The shipped prototype creates local JSON draft previews instead of changing the mailbox.

Modern supported equivalents are Get Email List / For Each Email for batch reading, and Send Email with Save as draft=True for draft creation. Original-thread/attachment forwarding is not implemented; notifications include the complaint text and ticket.

## Approve live test sends
1. First run with in_SendEnabled=False. Configure verified test inboxes in Routing.xlsx and the organization allowlist.
2. Inspect each Output/Drafts/*.json. Review exact To, Subject, Body, Organization and ActionID.
3. Obtain owner approval, then create Config/SendApproval.json with future UTC ExpiresUtc and approved Actions copied exactly from those JSON files. Use a short expiry. The example file is expired and approves nothing.
4. Rerun the same inbox batch with in_SendEnabled=True, in_UseSample=False. A dry-run audit does not block this promotion. New or changed email content is not covered by old approval and will be rejected.
5. Set in_SendEnabled=False after testing. Inspect State/Dispatch/*.json and the complaint log.

Each action writes Sending before the native send. Sent is written only after success. An exception leaves Uncertain and the complaint Failed, then the controller continues to the next complaint. Never automatically retry a non-idempotent send whose delivery is uncertain. Reconcile Gmail Sent and the journal manually. Retry limit is zero for uncertain sends; do not delete journals to bypass it. Approved actions already Sent are skipped.

Official references:
https://docs.uipath.com/activities/other/latest/productivity/google-workspace-email-get-email-list-connections
https://docs.uipath.com/activities/other/latest/productivity/google-workspace-email-for-each-email-connections
https://docs.uipath.com/activities/other/latest/productivity/google-workspace-email-send-email-connections
https://docs.uipath.com/activities/other/latest/productivity/google-workspace-output-object-properties
