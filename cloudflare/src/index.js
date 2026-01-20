import * as Sentry from "@sentry/cloudflare";
import { handleEmail } from "./email.js";

export default Sentry.withSentry(
  (env) => ({
    dsn: env.SENTRY_DSN,
    environment: env.ENVIRONMENT || "development",
    tracesSampleRate: 1.0,
  }),
  {
    async fetch(request, env, ctx) {
      const url = new URL(request.url);

      try {
        if (url.pathname === "/up") return new Response("OK", { status: 200 });
        return new Response("Not Found", { status: 404 });
      } catch (err) {
        console.error("Fetch error:", err);
        Sentry.captureException(err);
        throw err;
      }
    },

    async email(message, env, ctx) {
      try {
        await handleEmail(message, env);
      } catch (err) {
        console.error("Email error:", err);
        Sentry.captureException(err);
        throw err;
      }
    },
  }
);
