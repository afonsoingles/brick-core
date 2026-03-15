# this task receives a raw Cloudflare email-routed email for the printer email. 
# This should proccess the job, send to the printer/reply whatever.
def proccess_printer_email(request):
    from tools.printer import Printer
    from tools.users import UserTools
    from utils.mailer import Mailer
    from utils.storage import Storage
    from utils.ai import AI
    import os
    import json
    import base64
    import uuid


    
    printer = Printer()
    user_tools = UserTools()
    mailer = Mailer()
    ai = AI()
    storage = Storage()

    
    attachments = request.get("attachments")
    attachements_no_content = []
    for i in attachments:
        safe_attachment = i.copy()
        safe_attachment.pop("content", None)

        attachements_no_content.append(safe_attachment)

    safe_email = request
    safe_email["attachments"] = attachements_no_content

    ai_example_output = """
    {
        "name": "name",
        "email": "example@example.com",
        "files": [
            {
                "name": "example.pdf",
                "valid": true,
                "copies": 1,
                "color": true
            }
        ]
    }
    """
    ai_response = ai.get(f"""
You are a printer assistant. You will receive a JSON of an email below.
Based on the email's content, you should build a JSON payload of the necessary information. You should not start your response with '```json` or end with '```'. Just the pure JSON.
You will be sending an array (not list!) containing the following, and nothing else:
'name': The user's name (string). If one is not provided, try to determine it by the email address. If all else failed, set it to the first part of the email address (before the @).
'email': The user's email (string). This should be the email address that sent the email. There may be some cases where you get the sender as 'bounced-xxx...' or similar, but the headers provide the real senders email. In those cases, prefer the email that feels more like a real email address.
'files': A list of arrays. Each array should contain information about one file. You should provide the information below in one array:
    'name': The name of the file (string). It should be the same as the one sent for you to analyze.
    'valid': Whether the file is valid for printing or not (boolean). A file is valid if it is a PDF, otherwise its not.
    'copies': The number of copies that should be printed (integer). If its not specified a number, default to 1.
    'color': Whether the file should be printed in color or not (boolean). If its not specified, default to true.

Please note that the file's content itself (b64 enconded) will not be provided to you.
Here is an example of the JSON you should output:
{ai_example_output}

Here is the email JSON (input):
{json.dumps(safe_email)}""")
    ai_response = json.loads(ai_response)

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

    if user["suspended"]:
        return
    
    valid_files = ai_response["files"]
    invalid_files = []
    total_cost = 0
    set_pending = False
    for file in ai_response["files"]:
        if not file["valid"]:
            invalid_files.append(file)
            valid_files.remove(file)
            continue
        
        for attachment in attachments:
            if attachment["filename"] == file["name"]:
                file["content"] = attachment["content"]
                break
        
        total_cost += printer.calculate_cost(file["content"], color=file["color"], copies=file["copies"])
    
    
    if user["printer"]["credits"] < total_cost and user["printer"]["no_credits_action"] == "require_approval":
        mailer.send_email(
            sender_name="Brick Printer",
            sender_email=os.environ.get("PRINTER_EMAIL"),
            to=user["email"],
            subject="Your print job is on hold",
            template="not_enough_credits_en",
            name=user["name"],
            credits=user["printer"]["credits"],
            total_cost=total_cost
        )
        set_pending = True
        return
    elif user["printer"]["credits"] < total_cost and user["printer"]["no_credits_action"] != "require_approval":
        # This should never be happening. Adding this for a future implementation.
        return
    

    print_jobs = []
    for file in valid_files:
        job_status = "pending" if set_pending else "approved"
        file_str = f"printer_jobs/{str(uuid.uuid4())}.pdf"
        storage.upload_file(os.environ.get("S3_USER_CONTENT_BUCKET"), file_str, base64.b64decode(file["content"]))
        job = {
            "user_id": user["id"],
            "filename": file["name"],
            "file": file_str,
            "color": file["color"],
            "copies": file["copies"],
            "status": job_status
        }
        print_jobs.append(job)
    
    printer.register_bulk_jobs(print_jobs)