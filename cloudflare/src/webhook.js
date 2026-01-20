import { Sentry } from "./sentry";

export async function sendWebhook(body, headers, env) {
  const start = performance.now();

  try {
    const res = await fetch(env.WEBHOOK_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body,
    });

    const duration = performance.now() - start;

    Sentry.metrics.distribution(
      "webhook.latency_ms",
      duration
    );

    if (!res.ok) {
      Sentry.metrics.count("webhook.failed", 1);
      throw new Error(
        `Webhook failed (${res.status})`
      );
    }

    Sentry.metrics.count("webhook.sent", 1);
  } catch (err) {
    Sentry.metrics.count("webhook.failed", 1);
    Sentry.captureException(err);
    throw err;
  }
}
