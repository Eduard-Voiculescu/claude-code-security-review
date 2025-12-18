# API Code Audit Report: Intelligence Regression Investigation

**Date:** December 18, 2025
**Context:** inc-3542 - Investigation of perceived Opus 4.5 degradation
**Slack Thread:** https://anthropic.slack.com/archives/C0A4KRKN2L8/p1766073972263469

## Executive Summary

This audit reviewed the `claude-code-security-review` repository for API-side changes that could have contributed to intelligence regression in Claude Code. **No smoking gun was found in this repository that would directly cause the reported intelligence regression.** However, several observations are documented below.

## Repository Scope

This repository (`claude-code-security-review`) is a GitHub Action for AI-powered security review of pull requests using Claude. It is **not** the main Claude Code CLI or API infrastructure. Changes here would only affect:
- Security audit functionality when running this specific GitHub Action
- PR security scanning workflows

## Recent Code Changes Analyzed

### 1. Tool Restriction Change (Nov 25, 2025)
**Commit:** `505701d` - "Add --disallowed-tools for ps as extra hardening"

**Change:**
```python
# claudecode/github_action_audit.py:228
cmd = [
    'claude',
    '--output-format', 'json',
    '--model', DEFAULT_CLAUDE_MODEL,
    '--disallowed-tools', 'Bash(ps:*)'  # NEW
]
```

**Impact Assessment:** LOW
- Only restricts the `ps` command in bash
- Unlikely to affect general intelligence
- Security hardening, not a behavior change

### 2. Default Model Configuration
**File:** `claudecode/constants.py:8`

**Current Value:**
```python
DEFAULT_CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL') or 'claude-opus-4-1-20250805'
```

**Change History:** Model was updated from `claude-opus-4-20250514` to `claude-opus-4-1-20250805` in commit `beb0d9b` (Aug 7, 2025)

**Impact Assessment:** N/A for recent regression (change predates Dec 11)

### 3. Prompt Analysis

**Security Audit Prompt (`claudecode/prompts.py`):**
- No recent changes
- Contains detailed instructions for security analysis
- Includes appropriate confidence thresholds (>80% for flagging)
- Has proper exclusions for low-signal findings

**False Positive Filtering (`claudecode/claude_api_client.py:243-284`):**
- Extensive hard exclusion rules
- Could potentially over-filter findings
- No recent changes to these rules

### 4. Token Limits

**File:** `claudecode/constants.py:14`
```python
PROMPT_TOKEN_LIMIT = 16384  # 16k tokens max for claude-opus-4
```

**Observation:** This is relatively conservative. If prompts exceed this limit, responses may be truncated. However, this has been unchanged since initial release.

## Configuration Parameters Reviewed

| Parameter | Value | Location | Notes |
|-----------|-------|----------|-------|
| `DEFAULT_TIMEOUT_SECONDS` | 180 | constants.py:9 | 3 minutes |
| `DEFAULT_MAX_RETRIES` | 3 | constants.py:10 | Standard |
| `RATE_LIMIT_BACKOFF_MAX` | 30 | constants.py:11 | Reasonable |
| `SUBPROCESS_TIMEOUT` | 1200 | constants.py:22 | 20 minutes |
| `PROMPT_TOKEN_LIMIT` | 16384 | constants.py:14 | Conservative |

## API Client Behavior

The `ClaudeAPIClient` class (`claude_api_client.py`) implements:
- Retry logic with exponential backoff
- Rate limit handling
- Proper error handling

**No concerning patterns detected** that would cause intelligence regression.

## Findings Filter Analysis

The `FindingsFilter` class (`findings_filter.py`) uses two-stage filtering:
1. **Hard exclusion rules** - Pattern-based exclusions for common false positives
2. **Claude API filtering** - LLM-based analysis for remaining findings

The hard exclusion patterns (`HardExclusionRules`) filter:
- DOS/resource exhaustion
- Rate limiting recommendations
- Memory safety in non-C/C++ code
- Open redirects
- SSRF in HTML files

**Observation:** These rules are aggressive but appropriate for reducing false positives. No recent changes.

## Conclusion

### This Repository: No Regression Causes Found
Based on this audit, no changes in `claude-code-security-review` would cause the reported Opus 4.5 intelligence regression. The most recent code change (`--disallowed-tools` flag) is a minor security hardening measure.

### Cross-Reference with Slack Investigation
Per the Slack thread, the API team has already confirmed:
- No prompt changes for current models in the last ~2 weeks
- No new Claude Code A/B tests since Dec 11
- Potential root cause identified: "anti-laziness prompt" (PR #11406) - reverted Dec 18
- Clear NPS drop (-2 to -4 points) correlated with v2.0.62 release (Dec 8)

### Recommendations
1. **For this repository:** No action needed - changes are appropriate security measures
2. **For main investigation:** Focus on:
   - The reverted anti-laziness prompt (PR #11406)
   - Claude Code v2.0.62 release changes
   - Any system prompt modifications in the main Claude Code client

## Files Reviewed

- `claudecode/github_action_audit.py` - Main audit orchestration
- `claudecode/claude_api_client.py` - API client implementation
- `claudecode/prompts.py` - Prompt templates
- `claudecode/constants.py` - Configuration constants
- `claudecode/findings_filter.py` - Finding filtering logic
- `claudecode/audit.py` - Entry point
- `action.yml` - GitHub Action definition
- Git history since Dec 1, 2025

---
*Report generated as part of inc-3542 investigation*
