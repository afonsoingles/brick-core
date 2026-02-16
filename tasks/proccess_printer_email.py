# this task receives a raw Cloudflare email-routed email for the printer email. 
# This should proccess the job, send to the printer/reply whatever.
def proccess_printer_email(request):
    from tools.printer import Printer
    from tools.users import UserTools
    from utils.mailer import Mailer
    import os
    import base64


    
    printer = Printer()
    user_tools = UserTools()
    mailer = Mailer()

    
    sender = request.get("headers").get("sender")
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
        file_name = attachment.get("filename")

        if not content_b64:
            print(f"Attachment without content. from email: {sender} // file name: {file_name}")
            # skip attachments without content. this should never happen?
            continue

        if content_type != "application/pdf":
            mailer.send_email(
                sender_name="Brick Printer",
                sender=os.environ.get("PRINTER_EMAIL"),
                to=request.get("from"),
                subject="Not supported",
                template="printer_only_pdf_en",
                reply_id=request.get("headers").get("message-id"),
                references=request.get("headers").get("message-id")
            )
            continue

                

        try:
            data = base64.b64decode(content_b64)
        except Exception as e:
            print(f"Error decoding attachment: {e} // from email: {sender} // file name: {file_name}")
            continue
        
        user = user_tools.get_user_by_email(sender)

        if user == "not_found":
            user = user_tools.create_user(
                name=sender.split("@")[0],
                email=sender,
                password="",
                region="",
                language="EN",
                auth_methods=["otp"]
            )
            user = user_tools.get_user_by_email(sender)

        register = printer.register_print_job(
            user["id"],
            file_name=file_name,
            content=data,
        )

        if register == "pending":
            mailer.send_email(
                sender_name="Brick Printer",
                sender=os.environ.get("PRINTER_EMAIL"),
                to=request.get("from"),
                subject="Your print job is on hold",
                template="not_enough_credits_en",
                reply_id=request.get("headers").get("message-id"),
                references=request.get("headers").get("message-id")
            )

