---
name: "incident-postmortem-skill"
title: "Incident Postmortem Assistant (Repo Skill)"
description: "Collect CI run logs and related PR/commit context after a production failure and produce a draft postmortem with timeline, root cause analysis, and action items."
audience:
  - "AI-agent"
  - "SRE"
  - "DevOps-engineer"
owner: "team-platform@example.com"
stability: "experimental"
tags:
  - "postmortem"
  - "incident-response"
  - "runbooks"
last_updated: "2026-04-22"
inputs:
  - name: "run_id"
    type: "string"
    required: true
    description: "Workflow run ID or URL for the failed production job"
  - name: "environment"
    type: "string"
    required: true
    description: "env where failure occurred (prod|rel|qa)"
  - name: "collect_logs"
    type: "string"
    required: false
    description: "true|false — collect additional artifacts/logs"
secrets: []
outputs:
  - name: "postmortem_draft_path"
    type: "string"
    description: "Path to generated postmortem markdown"
  - name: "action_items_file"
    type: "string"
    description: "Path to suggested action items (todo list)"
---

### Incident Postmortem Assistant (Repo Skill)

Your goal is to gather CI workflow logs, correlate commits/PRs and service metrics where available, and draft a postmortem that includes a timeline, root cause analysis, and actionable remediation steps.

### Default approach
- Fetch workflow run logs and artifacts for the provided `run_id` and `environment`.
- Correlate the run with commits and PRs (author, reviewers, merge time) and list relevant changes.
- Produce a structured markdown postmortem: summary, timeline, impact, root cause, remediation, owners, and follow-up steps.

### Environment conventions
- Only trigger for `prod` or protected environments by default; for other envs allow manual triggers.

### Inputs / Outputs
- Inputs: `run_id`, `environment`, `collect_logs`.
- Outputs: `postmortem_draft_path`, `action_items_file`.

### Actions recommended
- Include clear, assignable action items with suggested owners and priorities.
- Attach relevant logs and links to PRs/commits in the draft for reviewer verification.
- Provide a short summary suitable for Slack/email and a longer detailed section for the incident tracker.

### Safety rules
- Sanitize logs for secrets before including them in the draft.
- Do not auto-post the postmortem to public channels; create a draft and open a PR or issue for review.

### Use these repo docs
- Devops/workflow-debugging-checklist.md
- Devops/troubleshooting-and-quality-gates.md

### Quick checklist
- Ensure `run_id` is valid and references the failing workflow run.
- Confirm logs attached do not contain secrets.
- Assign owners for the first two action items before publishing the draft.

### Example prompts
- "Draft a postmortem for workflow run 12345 in prod that failed during deployment; include timeline and 3 recommended action items."
 