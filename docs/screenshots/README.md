# Functional Image Sequence

These six generated panels present the current local API responses, mappings, and operating boundaries in the same order as the repository overview.

1. `01-system-flow.png`: sources, control stages, and outcomes.
2. `02-interface-surface.png`: named HTTP routes and service contract.
3. `03-core-processing.png`: contact input and mapped operation readback.
4. `04-event-guardrails.png`: duplicate and invalid-event handling.
5. `05-operating-readback.png`: accepted order and payment outcomes.
6. `06-validation-scope.png`: quality gates, current totals, and scope boundary.

Every image is generated at 1400 x 800, uses synthetic identifiers, excludes browser or provider chrome, and carries deterministic validation metadata. Tests enforce the exact names, dimensions, order, minimum rendered size, metadata, and public wording.

Regenerate after changing source fixtures, saved responses, README references, or generator copy:

```bash
python scripts/capture_screenshots.py
```
