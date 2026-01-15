import * as Sentry from '@sentry/cloudflare';

async function parseEmail(message) {
  const headers = {};
  let text;
  let html;
  const attachments = [];

  try {
    const emailText = await message.raw.text();
    
    // Parse headers from raw email
    const headerEndIndex = emailText.indexOf('\r\n\r\n');
    const headerSection = emailText.substring(0, headerEndIndex);
    const bodySection = emailText.substring(headerEndIndex + 4);

    // Parse headers
    headerSection.split('\r\n').forEach((line) => {
      const colonIndex = line.indexOf(':');
      if (colonIndex > -1) {
        const key = line.substring(0, colonIndex).toLowerCase().trim();
        const value = line.substring(colonIndex + 1).trim();
        headers[key] = value;
      }
    });

    // Simple MIME parsing for text/html extraction
    const textMatch = emailText.match(/\r?\n\r?\nContent-Type: text\/plain[\s\S]*?\r?\n\r?\n([\s\S]*?)(?=\r?\n--)/);
    if (textMatch) {
      text = textMatch[1].trim();
    }

    const htmlMatch = emailText.match(/Content-Type: text\/html[\s\S]*?\r?\n\r?\n([\s\S]*?)(?=\r?\n--)/);
    if (htmlMatch) {
      html = htmlMatch[1].trim();
    }

    // If no structured content found, use body section
    if (!text && !html) {
      text = bodySection;
    }
  } catch (error) {
    console.error('Error parsing email body:', error);
  }

  // Extract key fields from headers
  const from = message.from;
  const to = message.to?.split(',').map(e => e.trim()) || [];
  const cc = headers['cc']?.split(',').map(e => e.trim()) || [];
  const bcc = headers['bcc']?.split(',').map(e => e.trim()) || [];
  const subject = headers['subject'] || '';
  const messageId = headers['message-id'];
  const inReplyTo = headers['in-reply-to'];
  const references = headers['references']?.split(' ') || [];
  const date = headers['date'];

  return {
    from,
    to,
    cc: cc.length > 0 ? cc : undefined,
    bcc: bcc.length > 0 ? bcc : undefined,
    subject,
    text,
    html,
    headers,
    attachments,
    messageId,
    inReplyTo,
    references: references.length > 0 ? references : undefined,
    date,
  };
}

async function forwardToWebhook(emailData, webhookUrl) {
  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Brick-Email-Worker/1.0',
      },
      body: JSON.stringify(emailData),
    });

    if (!response.ok) {
      console.error(`Webhook returned status ${response.status}`);
      const text = await response.text();
      console.error(`Webhook response: ${text}`);
    }

    return response;
  } catch (error) {
    console.error('Error forwarding to webhook:', error);
    throw error;
  }
}

export default Sentry.withSentry(
  (env) => ({
    dsn: env.SENTRY_DSN,
    environment: env.ENVIRONMENT || 'development',
    enableLogs: true,
    sendDefaultPii: false,
  }),
  {
    async email(message, env, ctx) {
      Sentry.captureMessage(`Processing email from ${message.from} to ${message.to}`, 'info');
      Sentry.metrics.increment('email.processed', 1);

      try {
        const emailData = await parseEmail(message);
        
        const webhookResponse = await forwardToWebhook(emailData, env.WEBHOOK_URL);
        
        if (!webhookResponse.ok) {
          Sentry.captureMessage(
            `Failed to forward email: webhook returned ${webhookResponse.status}`,
            'warning'
          );
          Sentry.metrics.increment('email.webhook_failed', 1);
          Sentry.metrics.gauge('email.webhook_status_code', webhookResponse.status);
        } else {
          Sentry.captureMessage('Email successfully forwarded to webhook', 'info');
          Sentry.metrics.increment('email.webhook_success', 1);
        }
      } catch (error) {
        Sentry.captureException(error);
        Sentry.metrics.increment('email.error', 1);
        throw error;
      }
    },
  }
);
