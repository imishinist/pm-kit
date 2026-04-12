# Risk Management

## Risk Categories

- **Schedule**: Deadline delays, dependent task delays
- **Technical**: Technical uncertainty, performance issues
- **External**: Vendor dependencies, regulatory changes
- **Resource**: Staff shortages, skill gaps
- **Security**: Vulnerabilities, data leaks

## Priority Scoring

Priority = Urgency (1–3) × Impact (1–3)

- Urgency: 1 = Low, 2 = Medium, 3 = High
- Impact: 1 = Low, 2 = Medium, 3 = High

| Urgency \ Impact | 1 (Low) | 2 (Medium) | 3 (High) |
|-------------------|---------|------------|----------|
| 3 (High)          | 3       | 6          | **9**    |
| 2 (Medium)        | 2       | 4          | 6        |
| 1 (Low)           | 1       | 2          | 3        |

### Priority Levels

| Score | Level    | Action                          |
|-------|----------|---------------------------------|
| 7–9   | Critical | Immediate action required       |
| 4–6   | High     | Plan mitigation within the week |
| 2–3   | Medium   | Monitor and plan                |
| 1     | Low      | Accept or monitor               |

## Response Strategies

- **Avoid**: Eliminate the root cause of the risk
- **Mitigate**: Reduce probability or impact
- **Transfer**: Shift the risk to a third party (insurance, outsourcing, etc.)
- **Accept**: Acknowledge the risk and take no action

## File Format

Each risk is stored as a separate file in `risks/` with YAML frontmatter.

Filename: `RISK-<NNN>.md` (e.g. `RISK-001.md`)

```markdown
---
id: RISK-001
title: "API response time degradation"
category: Technical
urgency: 2
impact: 3
priority: 6
owner: Alice
status: open  # open | mitigating | closed
created: 2026-04-13
updated: 2026-04-13
---

## Description

Brief description of the risk.

## Mitigation

Actions being taken or planned.

## Notes

Updates, observations, status changes.
```

`risks/risk-register.md` serves as an index listing all risks with their current status.
