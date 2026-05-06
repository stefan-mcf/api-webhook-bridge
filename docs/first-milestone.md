# First Milestone Copy

Map one approved source event to the destination schema, run it against synthetic or approved sample data, return the validated output payload, audit log, retry/idempotency notes, and a handoff note. Live credential connection happens only after that proof slice is reviewed.

## Deliverables

- Source event field map.
- Synthetic or approved sample request.
- Deterministic response payload.
- Validation summary.
- Idempotency/retry note.
- Audit/dead-letter evidence if the sample is malformed.
- Handoff note explaining how to replay the slice.

## Boundary

No live credentials, live SaaS writes, real customer data, or cloud resources are needed for this first milestone unless separately approved.
