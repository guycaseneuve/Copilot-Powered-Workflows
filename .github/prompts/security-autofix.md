# Security Report — Output Template

Generate a security scan report in markdown using the sections below. Base your analysis on the aggregated findings JSON provided.

## Instructions

1. Analyze the findings by severity and vulnerability class.
2. Provide remediation priority based on exploitability and business risk.
3. Indicate which findings are auto-fixable vs require manual code changes.

---

## Output Format (use these exact sections)

### Executive Summary

One paragraph (3-5 sentences) suitable for Slack/email. State: number of findings, highest severity, most critical issue, and recommended immediate action.

### Scan Overview

| Metric | Value |
|---|---|
| Repository | `{REPO}` |
| Scan Date | `{SCAN_DATE}` |
| Total Findings | (count) |
| Critical | (count) |
| High | (count) |
| Medium | (count) |
| Low | (count) |
| Auto-fixable | (count) |

### Critical & High Findings

For each critical/high finding, provide:

#### [Severity] Rule ID — Short description

- **File:** `path/to/file.js:line`
- **Scanner:** CodeQL / Dependabot
- **Description:** What the vulnerability is
- **Impact:** What an attacker could do
- **Remediation:** Specific fix (code pattern or version upgrade)
- **Auto-fixable:** Yes/No

### Medium & Low Findings

Summarize in a table:

| Severity | File | Rule | Description | Auto-fix |
|---|---|---|---|---|
| Medium | `file.js:10` | rule-id | Brief description | Yes/No |

### Remediation Priority

Ordered list of recommended actions:
1. (highest priority action)
2. ...
3. ...

### Auto-fix Summary

List what `npm audit fix` and `eslint --fix` will resolve automatically:
- **npm audit fix:** (list of packages that will be upgraded)
- **eslint --fix:** (list of style issues that will be corrected)
- **Manual fixes required:** (list of issues needing code changes)
