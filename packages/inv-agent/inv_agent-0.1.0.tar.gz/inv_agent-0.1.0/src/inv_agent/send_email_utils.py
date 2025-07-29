import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from logger import log

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")
SUPPLIER_EMAIL = os.getenv("SUPPLIER_EMAIL")
DEFAULT_RECEIVER = os.getenv("RECEIVER_EMAIL")

def send_email(
    subject: str,
    body: str,
    recipient_type: str = "manager",
    attachment_path: str = None
) -> str:
    """
    Send an email with or without a file attachment.

    Args:
        subject (str): Subject of the email.
        body (str): Plain text body content.
        recipient_type (str): One of 'manager', 'provider', or 'custom'.
        attachment_path (str): Full path to file to attach (optional).
    
    Returns:
        str: about the status of execution.
    """

    if not all([SENDER_EMAIL, SENDER_PASSWORD]):
        log("Email Sending Failed", "Sender email or password not configured")
        return "No sender details"

    if recipient_type == "manager":
        receiver_email = MANAGER_EMAIL
    elif recipient_type == "supplier":
        receiver_email = SUPPLIER_EMAIL
    else:
        receiver_email = DEFAULT_RECEIVER

    if not receiver_email:
        log("Email Sending Failed", f"No receiver email configured for type '{recipient_type}'")
        return "No receiver info"

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachment_path:
            if not os.path.exists(attachment_path):
                log("Attachment Error", f"File does not exist: {attachment_path}")
                return "No file to attach"

            try:
                with open(attachment_path, "rb") as file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}"
                )
                msg.attach(part)
            except Exception as e:
                log("Attachment Error", f"Failed to attach file: {attachment_path}, Error: {str(e)}")
                return "Failed to attach file"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        log("Email Sent", f"Subject: {subject}, To: {receiver_email}")
        return f"Email Sent to {receiver_email}"

    except Exception as e:
        log("Email Sending Failed", f"Subject: {subject}, To: {receiver_email}, Error: {str(e)}")
        return "Failed to send mail"