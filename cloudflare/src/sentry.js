let initialized = false;
let SentryInstance = null;

/**
 * Initialize Sentry dynamically at runtime
 * Returns the Sentry instance for use in other modules
 */
export async function getSentry(env, ctx) {
  if (initialized) return SentryInstance;
  if (!env.SENTRY_DSN || env.ENVIRONMENT !== "production") return null;

  // Dynamic import to avoid Wrangler ESM warning
  const Sentry = await import("@sentry/cloudflare");

  Sentry.init({
    dsn: env.SENTRY_DSN,
    environment: env.ENVIRONMENT,
    tracesSampleRate: 1.0,
  });

  if (ctx) {
    ctx.waitUntil(
      Sentry.flush(2000).catch((err) =>
        console.error("Sentry flush failed", err)
      )
    );
  }

  initialized = true;
  SentryInstance = Sentry;
  return SentryInstance;
}
