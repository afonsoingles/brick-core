# this task receives a raw Cloudflare email-routed email for the printer email. 
# This should proccess the job, send to the printer/reply whatever.
def proccess_printer_email(request):
    from tools.printer import Printer
    from tools.users import UserTools
    from utils.mailer import Mailer
    from utils.ai import AI
    import os
    import json
    import base64


    
    printer = Printer()
    user_tools = UserTools()
    mailer = Mailer()
    ai = AI()

    
    sender = request.get("headers").get("from")
    attachments = request.get("attachments")
    attachements_no_content = []
    for i in attachments:
        i["content"] = ""
        attachements_no_content.append(i)

    safe_email = request
    safe_email["attachments"] = attachements_no_content

    ai_response = ai.get(f"""
You are a printer assistant. You will receive a JSON of an email below.
Based on the email's content, you build a JSON payload of the necessary information.
You will be sending an array containing the following:
'name': The user's name (string). If one is not provided, try to determine it by the email address. If all else failed, set it to the first part of the email address (before the @).
'email': The user's email (string). This should be the email address that sent the email.
'files': A list of arrays. Each array should contain information about one file. You should provide the information below in one array:
    'name': The name of the file (string). It should be the same as the one sent for you to analyze.
    'valid': Whether the file is valid for printing or not (boolean). A file is valid if it is a PDF, otherwise its not.
    'copies': The number of copies that should be printed (integer). If its not specified a number, default to 1.
    'color': Whether the file should be printed in color or not (boolean). If its not specified, default to true.

Please note that the file's content itself (b64 enconded) will not be provided to you.

Here is the email JSON:
{json.dumps(safe_email)}""")
    
    ai_response = json.loads(ai_response)
    print(ai_response)

    user = user_tools.get_user_by_email(ai_response["email"])
    if user == "not_found":
        user_tools.create_user(
            name=ai_response["name"],
            email=ai_response["email"],
            auth_methods=["otp"],
            region="INTL",
            language="EN"
        )
        user = user_tools.get_user_by_email(ai_response["email"])

    invalid_files = []
    for file in ai_response["files"]:
        if file["valid"]:

            printer.register_print_job(
                user_id=user["id"],
                file_name=file["name"],
                copies=file["copies"],
                color=file["color"]
            )
        else:
            invalid_files.append(file["name"])
    
    if len(invalid_files) > 0:
        # TODO: Actually list what files are invalid.
        mailer.send_email(
            sender_name="Brick Printer",
            sender=os.environ.get("PRINTER_EMAIL"),
            to=ai_response["email"],
            subject="Invalid files for printing",
            template="printer_only_pdf"
            
        )