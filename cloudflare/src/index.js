import { handleEmail } from "./email";
import { initSentry } from "./sentry";

export default {
  async fetch(request, env, ctx) {
    const Sentry = await initSentry(env, ctx);

    const url = new URL(request.url);

    try {
      if (url.pathname === "/up") return new Response("OK", { status: 200 });
      return new Response("Not Found", { status: 404 });
    } catch (err) {
      Sentry?.captureException(err);
      throw err;
    }
  },

  async email(message, env, ctx) {
    const Sentry = await initSentry(env, ctx);

    try {
      await handleEmail(message, env);
    } catch (err) {
      Sentry?.captureException(err);
      throw err;
    }
  },
};
