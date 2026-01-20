import { signPayload } from "./signer";
import { sendWebhook } from "./webhook";
import { Sentry } from "./sentry";

export async function handleEmail(message, env) {
  Sentry.metrics.count("email.received", 1);

  const rawEmail = await message.raw();
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
    raw: btoa(
      String.fromCharCode(...new Uint8Array(rawEmail))
    ),
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
