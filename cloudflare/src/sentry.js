import * as Sentry from "@sentry/cloudflare";

export function initSentry(env) {
  if (!env.SENTRY_DSN) return null;
  return Sentry;
}

export { Sentry };
