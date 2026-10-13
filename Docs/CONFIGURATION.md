# Configure routes, FAQ, approval and AI

## Routing.xlsx
Edit the first worksheet. The reader uses the first worksheet and row 1 headers; keep the required columns. One Organization+Category row must exist per route. Duplicate keys require manual review. Department may be changed to an authorized team's name, including Delivery and Logistics; routing always uses this table instead of an AI department guess. Set DepartmentEmail and EscalationEmail to inboxes that you own or have authorization to use. Set Active=True only after verification. Demo addresses are blank.

## Organization recipient authorization
Config/AuthorizedRecipients.json example shape (replace, do not send to this placeholder):
[{"Organization":"Flipkart","Email":"your-owned-test-inbox@example.invalid"}]

Replace the placeholder with an actual approved test inbox. One address can be reused across multiple organizations only when explicitly listed for each organization. This is a local authorization control; only trusted admins should edit configuration. It does not implement separate organization login accounts or enterprise RBAC.

ManualReviewRecipients.json has the same shape. Add an Unknown entry for an authorized central review queue if needed and also put it in AuthorizedRecipients.json. Unknown never inherits another company's address. Without that configuration, review stays in the local log. Urgent known-company complaints use their own authorized EscalationEmail. When department and escalation recipient are the same, one escalation notification is prepared.

## FAQ_KnowledgeBase.xlsx
Exactly one organization/category match is required to recommend ApprovedResponse. Multiple or missing rows recommend manual review. EscalationRequired=True raises the escalation flag. Templates must be reviewed by the participating organization before operational use. No refund deadline, warranty eligibility or policy is promised by default.

## Optional AI
Default: in_AIEnabled=False, in_AIApproved=False. Rules are always evaluated first. To approve a call, set both flags True, configure Config/AI.json with your approved HTTPS gateway and set its key as a Windows environment variable RESOLVEX_AI_KEY. Never put the key in Excel, XAML or GitHub. The gateway receives JSON with organization, subject, text, allowedCategories and instruction and must return the exact object described by AI-response.schema.json directly (not a provider chat-completions envelope). No gateway service is deployed in this package.

Response fields: Organization, Category, Department, Sentiment, Priority, Confidence, Summary, SuggestedResponse. Unknown fields, invalid enums, changed organization, oversized text, malformed JSON and confidence out of range are rejected; unavailable/invalid responses fall back to rules. Confidence below configurable threshold (default 0.75) requires manual review. AI cannot rescue missing/ambiguous companies. Department from AI is validated but table mapping remains authoritative. AI SuggestedResponse is not used for outgoing content; FAQ is authoritative. AI calls are skipped when rules already require manual review in this prototype.

Rule Confidence is a scoring heuristic, not a calibrated probability. Rule baseline sentiment and priority are phrase-based and do not implement robust negation or sarcasm handling. The rule severity floor can raise AI severity but cannot downgrade Critical to Low. Review safety-critical input manually.

## Persistence and privacy
State/Audit.json is the durable upserted audit and is recovered on the next run. Output XLSX is a materialized report. State/Dispatch contains per-action send journals. Close Excel while running; workbook locks may block report writing. Logging failure is never treated as successful processing. Do not reset State casually. Reset sample data only by using a fresh extracted copy.

ComplaintText and CustomerEmail are stored because they are required audit columns; protect local folders. Failure logs contain only ticket/time/exception type. Disable verbose activity logging of input/output arguments and mark sensitive activities Private in Studio before real intake. Never upload Output, State, approval/configured recipients or customer samples to the public repository.
