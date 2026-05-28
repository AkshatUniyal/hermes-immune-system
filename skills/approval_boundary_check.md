---
name: approval-boundary-check
description: Detect actions that require human approval, such as sending, deleting, exporting, updating, publishing, or writing memory.
---

# Approval Boundary Check

Use this skill before an agent takes an action outside read-only analysis.

## Approval Required

- External sends.
- Raw exports.
- Deletes or production updates.
- Persistent memory writes.
- Issue comments that expose restricted content.
- Any release of credentials or secrets.

## Safe Response

Convert risky actions into drafts or dry-run plans and request human approval.

