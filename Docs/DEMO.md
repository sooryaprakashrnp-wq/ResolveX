# Hackathon demo (dry run first)

1. Open a fresh downloaded project in Studio. Run Validate Project.
2. Run Main with sample=True, sending=False and AI=False. No Gmail connection is required for this local sample.
3. Open Output/Complaints_Log.xlsx and locate demo-001 through demo-005. Expected organization/category/department:

| Message | Organization | Category | Department |
|---|---|---|---|
| demo-001 | Flipkart | Order/Delivery | Order Support |
| demo-002 | Samsung | Warranty | Warranty and Service |
| demo-003 | Amazon | Refund | Payments and Refunds |
| demo-004 | Airtel | Technical | Technical Support |
| demo-005 | Unknown | Returns | Manual Review |

4. Explain RouteUnconfigured: no real company emails were invented; demo addresses must be explicitly configured. This is expected before verified test inbox setup.
5. Show duplicate demo-001 appears once (13 unique message IDs out of 14 sample entries). Show company ambiguity, equal category scores, empty body and critical/high priority cases.
6. Open Output/Priority_Report.xlsx. It contains at most five logged complaints, Critical first, then High, Medium, Low; older receipt first within a severity. All logged complaints are eligible because forwarding is not resolution. No resolution tracking is implemented.
7. Rerun the same sample: upserted audit retains 13 rows, already audited dry-run rows are skipped.
8. For Gmail demonstration, bind native adapters using the existing project and connection, send test complaints manually to that inbox, and keep in_SendEnabled=False. Show resulting local drafts and audit.
9. Only with owner approval, configure test recipients, create exact SendApproval.json, enable sending and show a confirmed Sent row. Do not claim live sending during a local-only demo.

Suggested presentation: "ResolveX identifies organization separately from category, scores all matching keywords, routes through verified per-organization mappings, and grounds response recommendations in approved FAQ. Optional AI is validated and cannot choose a recipient. Journals prevent duplicate or uncertain resend."
