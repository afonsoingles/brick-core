import { signPayload } from "./signer.js";
import { sendWebhook } from "./webhook.js";
import { Sentry } from "./sentry.js";

export async function handleEmail(message, env) {
  Sentry?.metrics?.count("email.received", 1);

  const rawSize = rawEmail.byteLength;

  Sentry.metrics.distribution(
    "email.size_bytes",
    rawSize
  );

  const payload = {
    from: message.from,
    to: message.to,
    subject: message.headers.get("subject") ?? "",
    text: await message.text(),
    received_at: new Date().toISOString(),
  };

  const body = JSON.stringify(payload);
  const timestamp = Date.now().toString();

  const signature = await signPayload(
    body,
    timestamp,
    env.SIGNING_PRIVATE_KEY
  );

  await sendWebhook(
    body,
    {
      "X-Signature": signature,
      "X-Timestamp": timestamp,
    },
    env
  );
}
