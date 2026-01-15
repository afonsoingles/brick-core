# Cloudflare Worker

Hi! This worker is responsible for forwarding emails from Cloudflare to Brick. It is automatically deployed to Cloudflare Workers via GH Actions.

You will need to set the `WEBHOOK_URL`, `SENTRY_DSN`, and `BRICK_WEBHOOK_TOKEN` in the Cloudflare Dashboard.

~ Afonso (01/15/2026)