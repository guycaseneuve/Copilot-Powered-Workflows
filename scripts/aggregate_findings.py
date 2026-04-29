#!/usr/bin/env python3
"""
aggregate_findings.py — Parse SARIF (CodeQL) and JSON (Dependabot) scan results,
deduplicate by (file, rule, line), sort by severity, output unified JSON.

Usage:
    python aggregate_findings.py \
        --sarif results/codeql.sarif \
        --dependabot results/dependabot.json \
        --output results/aggregated-findings.json

Output schema:
{
  "summary": { "total": N, "critical": N, "high": N, "medium": N, "low": N },
  "findings": [
    {
      "file": "path/to/file.js",
      "line": 42,
      "rule": "js/sql-injection",
      "severity": "critical",
      "scanner": "codeql",
      "message": "...",
      "suggestion": "..."
    }
  ]
}
"""

import argparse
import json
import sys
from pathlib import Path

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "note": 4}

# Map SARIF level + CodeQL precision to our severity
SARIF_SEVERITY_MAP = {
    "error": "high",
    "warning": "medium",
    "note": "low",
}

# CodeQL rules that are critical regardless of SARIF level
CRITICAL_RULES = {
    "js/sql-injection",
    "js/command-line-injection",
    "js/code-injection",
    "js/unsafe-deserialization",
}

HIGH_RULES = {
    "js/path-injection",
    "js/reflected-xss",
    "js/stored-xss",
    "js/hardcoded-credentials",
    "js/prototype-polluting-assignment",
}


def parse_sarif(sarif_path: Path) -> list[dict]:
    """Parse a SARIF file and extract findings."""
    findings = []
    with open(sarif_path, "r", encoding="utf-8") as f:
        sarif = json.load(f)

    for run in sarif.get("runs", []):
        tool_name = run.get("tool", {}).get("driver", {}).get("name", "codeql")
        rules_map = {}
        for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
            rules_map[rule["id"]] = rule

        for result in run.get("results", []):
            rule_id = result.get("ruleId", "unknown")
            level = result.get("level", "warning")

            # Determine severity
            if rule_id in CRITICAL_RULES:
                severity = "critical"
            elif rule_id in HIGH_RULES:
                severity = "high"
            else:
                severity = SARIF_SEVERITY_MAP.get(level, "medium")

            # Extract location
            locations = result.get("locations", [])
            file_path = "unknown"
            line = 0
            if locations:
                phys = locations[0].get("physicalLocation", {})
                artifact = phys.get("artifactLocation", {})
                file_path = artifact.get("uri", "unknown")
                region = phys.get("region", {})
                line = region.get("startLine", 0)

            # Extract message
            message = result.get("message", {}).get("text", "")

            # Get suggestion from rule help if available
            suggestion = ""
            rule_meta = rules_map.get(rule_id, {})
            if rule_meta:
                help_text = rule_meta.get("help", {}).get("text", "")
                if help_text:
                    suggestion = help_text[:200]

            findings.append({
                "file": file_path,
                "line": line,
                "rule": rule_id,
                "severity": severity,
                "scanner": tool_name.lower(),
                "message": message,
                "suggestion": suggestion,
            })

    return findings


def parse_dependabot(dependabot_path: Path) -> list[dict]:
    """Parse Dependabot alerts JSON and extract findings."""
    findings = []
    with open(dependabot_path, "r", encoding="utf-8") as f:
        alerts = json.load(f)

    # Handle both array of alerts and object with alerts key
    if isinstance(alerts, dict):
        alerts = alerts.get("alerts", alerts.get("data", []))

    for alert in alerts:
        # GitHub Dependabot alert structure
        security_advisory = alert.get("security_advisory", {})
        severity_str = (
            alert.get("security_vulnerability", {}).get("severity", "")
            or security_advisory.get("severity", "medium")
        ).lower()

        # Normalize severity
        if severity_str in SEVERITY_ORDER:
            severity = severity_str
        else:
            severity = "medium"

        # Extract package info
        dep = alert.get("dependency", {})
        package_name = dep.get("package", {}).get("name", "unknown")
        manifest_path = dep.get("manifest_path", "package.json")

        # CVE and description
        cve_id = ""
        identifiers = security_advisory.get("identifiers", [])
        for ident in identifiers:
            if ident.get("type") == "CVE":
                cve_id = ident.get("value", "")
                break

        summary = security_advisory.get("summary", alert.get("title", ""))
        description = security_advisory.get("description", "")

        # Fix version
        first_patched = (
            alert.get("security_vulnerability", {})
            .get("first_patched_version", {})
            .get("identifier", "")
        )
        suggestion = f"Upgrade {package_name} to >= {first_patched}" if first_patched else ""

        rule = cve_id or f"dependabot/{package_name}"

        findings.append({
            "file": manifest_path,
            "line": 0,
            "rule": rule,
            "severity": severity,
            "scanner": "dependabot",
            "message": f"{package_name}: {summary}",
            "suggestion": suggestion,
        })

    return findings


def deduplicate(findings: list[dict]) -> list[dict]:
    """Deduplicate findings by (file, rule, line). Keep highest severity."""
    seen = {}
    for f in findings:
        key = (f["file"], f["rule"], f["line"])
        if key in seen:
            existing = seen[key]
            # Keep the one with higher severity
            if SEVERITY_ORDER.get(f["severity"], 4) < SEVERITY_ORDER.get(existing["severity"], 4):
                seen[key] = f
            # Note cross-scanner validation
            if f["scanner"] != existing["scanner"]:
                seen[key]["scanner"] = f"{existing['scanner']},{f['scanner']}"
        else:
            seen[key] = f
    return list(seen.values())


def sort_by_severity(findings: list[dict]) -> list[dict]:
    """Sort findings by severity (critical first)."""
    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 4))


def build_summary(findings: list[dict]) -> dict:
    """Build summary statistics."""
    summary = {"total": len(findings), "critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f["severity"]
        if sev in summary:
            summary[sev] += 1
    return summary


def main():
    parser = argparse.ArgumentParser(description="Aggregate security scan findings")
    parser.add_argument("--sarif", type=str, help="Path to CodeQL SARIF file", default=None)
    parser.add_argument("--dependabot", type=str, help="Path to Dependabot alerts JSON", default=None)
    parser.add_argument("--output", type=str, required=True, help="Output path for aggregated JSON")
    args = parser.parse_args()

    all_findings = []

    if args.sarif and Path(args.sarif).exists():
        print(f"Parsing SARIF: {args.sarif}")
        sarif_findings = parse_sarif(Path(args.sarif))
        print(f"  Found {len(sarif_findings)} findings from CodeQL")
        all_findings.extend(sarif_findings)
    else:
        print("No SARIF file provided or file not found — skipping CodeQL results")

    if args.dependabot and Path(args.dependabot).exists():
        print(f"Parsing Dependabot: {args.dependabot}")
        dep_findings = parse_dependabot(Path(args.dependabot))
        print(f"  Found {len(dep_findings)} findings from Dependabot")
        all_findings.extend(dep_findings)
    else:
        print("No Dependabot file provided or file not found — skipping Dependabot results")

    if not all_findings:
        print("No findings from any scanner.")
        result = {"summary": build_summary([]), "findings": []}
    else:
        deduped = deduplicate(all_findings)
        sorted_findings = sort_by_severity(deduped)
        result = {"summary": build_summary(sorted_findings), "findings": sorted_findings}
        print(f"\nAggregated: {result['summary']['total']} unique findings")
        print(f"  Critical: {result['summary']['critical']}")
        print(f"  High:     {result['summary']['high']}")
        print(f"  Medium:   {result['summary']['medium']}")
        print(f"  Low:      {result['summary']['low']}")

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nOutput written to: {output_path}")


if __name__ == "__main__":
    main()
