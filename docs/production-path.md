# Production Path After Local Proof

This repo proves the local integration pattern. A real deployment would be separately scoped.

## Steps after approval

1. Confirm source event schema and destination schema with the client.
2. Add scoped credentials through a secret manager or approved environment mechanism.
3. Use a durable idempotency store such as Redis, Postgres, Airtable, or the destination's native idempotent upsert key.
4. Add retry/backoff policy and dead-letter review queue.
5. Add structured logs and operational alerting.
6. Run one staging replay with approved sample data.
7. Prepare rollback and disable switch.
8. Run the first live event only after client review.

## Non-claim

The local proof does not claim live Shopify, Stripe, Airtable, HubSpot, Slack, cloud deployment, or production operation.
