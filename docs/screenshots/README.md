# Functional Image Sequence

These six generated panels present the current local API responses, mappings, and operating boundaries in the same order as the repository overview.

1. [System flow](01-system-flow.png): sources, control stages, and outcomes.
2. [Interface surface](02-interface-surface.png): named HTTP routes and service contract.
3. [Core processing](03-core-processing.png): contact input and mapped operation readback.
4. [Event guardrails](04-event-guardrails.png): duplicate and invalid-event handling.
5. [Operating readback](05-operating-readback.png): accepted order and payment outcomes.
6. [Validation and scope](06-validation-scope.png): recorded quality gates and scope.

These are generated local panels rather than native provider screens. Their
recorded check totals may precede the current revision; use current CI for the
latest result.

Every image is generated at 1400 x 800, uses synthetic identifiers, excludes browser or provider chrome, and carries deterministic validation metadata. Tests enforce the exact names, dimensions, order, minimum rendered size, metadata, and public wording.

Regenerate after changing source fixtures, saved responses, README references, or generator copy:

```bash
python scripts/capture_screenshots.py
```
