import requests
import os

class Mailer:
    def _load_template(self, template, **vars):
        path = os.path.join("mailers", f"{template}.txt")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content.format(**vars)

    def send_email(self, sender_name="", sender=None, subject="", template=None, to=None, reply_id=None, references=None, **vars):
        text = self._load_template(template, **vars)
        if reply_id and references:
            extra = {
                "h:In-Reply-To": reply_id,
                "h:References": references
            }
        else:
            extra = {}

        return requests.post(
            f"https://api.eu.mailgun.net/v3/{os.environ.get('MAILGUN_DOMAIN')}/messages",
            auth=("api", os.environ.get("MAILGUN_API_KEY")),
            data={
                "from": f"{sender_name} <{sender}>",
                "to": to,
                "subject": subject,
                "text": text,
                **extra
            }
        ).json()