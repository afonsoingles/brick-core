# this task receives a raw Cloudflare email-routed email for the printer email. 
# This should proccess the job, send to the printer/reply whatever.
def proccess_printer_email(request):
    from utils.printer import Printer
    from utils.mailer import Mailer
    import os
    import base64


    
    printer = Printer()
    mailer = Mailer()

    if not str(request.get("from")).lower().endswith("@afonsoingles.dev"):
        # temporary solution while i don't implement users.
        mailer.send_email(
            sender_name="Brick Printer",
            sender=os.environ.get("PRINTER_EMAIL"),
            to=request.get("from"),
            subject="Não autorizado",
            template="general_not_allowed_pt",
            reply_id=request.get("headers").get("message-id"),
            references=request.get("headers").get("message-id")
        )
        return
    
    attachments = request.get("attachments")

    if not attachments:

        mailer.send_email(
            sender_name="Brick Printer",
            sender=os.environ.get("PRINTER_EMAIL"),
            to=request.get("from"),
            subject="Falha na impressão",
            template="printer_no_attachments_pt",
            reply_id=request.get("headers").get("message-id"),
            references=request.get("headers").get("message-id")
        )

        return

    for attachment in attachments:
        content_b64 = attachment.get("content") 
        content_type = attachment.get("contentType")

        if not content_b64:
            # skip attachments without content. this should never happen?
            continue

        if content_type != "application/pdf":
            mailer.send_email(
                sender_name="Brick Printer",
                sender=os.environ.get("PRINTER_EMAIL"),
                to=request.get("from"),
                subject="Não suportado",
                template="printer_only_pdf_pt",
                reply_id=request.get("headers").get("message-id"),
                references=request.get("headers").get("message-id")
            )
            continue

                

        try:
            data = base64.b64decode(content_b64)
        except Exception as e:
            # email reply
            continue

        printer.print_data(data, job_name="brick_print_job")
