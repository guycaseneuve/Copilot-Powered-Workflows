# Incident Postmortem — Output Template

Generate a structured incident postmortem in markdown using the sections below.

## Instructions

1. Analyze the failed workflow run logs to identify the root cause.
2. Correlate with recent commits and PRs to trace what introduced the failure.
3. Produce a clear timeline and actionable remediation plan.

---

## Output Format (use these exact sections)

### Title

`Incident Postmortem: [Environment] — [Short failure description]`

### Summary (Slack-ready)

2-3 sentences suitable for posting to Slack/email. State: what failed, when, impact, and current status.

### Timeline

| Time (UTC) | Event |
|---|---|
| HH:MM | First relevant event |
| HH:MM | Failure detected |
| HH:MM | Investigation started |
| HH:MM | Root cause identified |
| HH:MM | Resolution applied |

### Impact Assessment

- **Environment:** {ENVIRONMENT}
- **Duration:** estimated downtime or degraded period
- **Affected services:** list of impacted services/endpoints
- **User impact:** description of user-facing effects
- **Data impact:** any data loss or corruption (if applicable)

### Root Cause Analysis

Detailed explanation of what went wrong. Include:
- The specific change or condition that triggered the failure
- Why existing safeguards (tests, validations) did not catch it
- Contributing factors (environment config, timing, dependencies)

### Correlated Changes

| PR/Commit | Author | Merged | Relevant? |
|---|---|---|---|
| PR #N or commit SHA | author | timestamp | Yes/No + why |

### Remediation Steps

What was done (or should be done) to resolve the immediate issue:
1. Step taken/needed
2. ...

### Action Items

| Priority | Action | Owner | Due |
|---|---|---|---|
| P0 | Immediate fix description | @assignee | Date |
| P1 | Preventive measure | @assignee | Date |
| P2 | Process improvement | @assignee | Date |

### Lessons Learned

- What went well during incident response
- What could be improved
- Process or tooling gaps identified

### Follow-up Schedule

- [ ] Day 1: Verify fix in production
- [ ] Day 3: Review action item progress
- [ ] Day 7: Close out postmortem if all P0/P1 items resolved
