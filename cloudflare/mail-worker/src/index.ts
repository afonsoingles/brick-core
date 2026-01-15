import { EmailMessage } from 'cloudflare:email';
import { createMimeParser } from 'mailparser';

interface EmailData {
  from: string;
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  text?: string;
  html?: string;
  headers: Record<string, string>;
  attachments: Array<{
    filename: string;
    contentType: string;
    size: number;
    content: string; // base64 encoded
  }>;
  messageId?: string;
  inReplyTo?: string;
  references?: string[];
  date?: string;
}

interface Env {
  WEBHOOK_URL: string;
}

async function parseEmail(message: EmailMessage): Promise<EmailData> {
  const headers: Record<string, string> = {};
  
  // Extract headers
  message.headers.forEach((value, key) => {
    headers[key.toLowerCase()] = value;
  });

  const from = message.from;
  const to = message.to?.split(',').map(e => e.trim()) || [];
  const cc = headers['cc']?.split(',').map(e => e.trim()) || [];
  const bcc = headers['bcc']?.split(',').map(e => e.trim()) || [];
  const subject = message.headers.get('subject') || '';
  const messageId = message.headers.get('message-id');
  const inReplyTo = message.headers.get('in-reply-to');
  const references = message.headers.get('references')?.split(' ') || [];
  const date = message.headers.get('date');

  // Parse email body
  let text: string | undefined;
  let html: string | undefined;
  const attachments: EmailData['attachments'] = [];

  try {
    const rawEmail = await message.raw();
    const emailText = await rawEmail.text();

    // Simple MIME parsing for text/html extraction
    // Note: For production, consider using a more robust MIME parser
    const textMatch = emailText.match(/\r?\n\r?\nContent-Type: text\/plain[\s\S]*?\r?\n\r?\n([\s\S]*?)(?=\r?\n--)/);
    if (textMatch) {
      text = textMatch[1].trim();
    }

    const htmlMatch = emailText.match(/Content-Type: text\/html[\s\S]*?\r?\n\r?\n([\s\S]*?)(?=\r?\n--)/);
    if (htmlMatch) {
      html = htmlMatch[1].trim();
    }

    // If no structured content found, try to get body differently
    if (!text && !html) {
      // Extract everything after headers
      const parts = emailText.split(/\r?\n\r?\n/);
      if (parts.length > 1) {
        text = parts.slice(1).join('\n');
      }
    }
  } catch (error) {
    console.error('Error parsing email body:', error);
  }

  const emailData: EmailData = {
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

  return emailData;
}

async function forwardToWebhook(emailData: EmailData, webhookUrl: string): Promise<Response> {
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

export default {
  async email(message: EmailMessage, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log(`Processing email from ${message.from} to ${message.to}`);

    try {
      const emailData = await parseEmail(message);
      
      console.log(`Forwarding email to webhook: ${env.WEBHOOK_URL}`);
      const webhookResponse = await forwardToWebhook(emailData, env.WEBHOOK_URL);
      
      if (!webhookResponse.ok) {
        console.error(`Failed to forward email: webhook returned ${webhookResponse.status}`);
        // Optionally: reject the email or handle retry logic
      } else {
        console.log('Email successfully forwarded to webhook');
      }
    } catch (error) {
      console.error('Error processing email:', error);
      // You may want to reject the email or store it for retry
      throw error;
    }
  },
} satisfies ExportedHandler<Env>;
