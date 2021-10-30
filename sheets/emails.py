import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


class Emails:
    # Import the account and password from lib.cft.cft probably
    def __init__(self, account: str, password: str):
        self.account = account
        self.password = password

    def send_email(self, message: MIMEMultipart, recipients: list):
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com")
            server.ehlo()
            server.login(self.account, self.password)
            server.sendmail(self.account, recipients, message.as_string())
        except smtplib.SMTPServerDisconnected:
            pass

    def create_message(
        self,
        recipients: list,
        email_data: dict,
        student,
        class_code,
    ):
        # Note: the plain text one is only there in case someone is using
        # an email client that doesn't support html emails, or they turned
        # it off for some reason.
        text_path = Path(__file__).parent / email_data["text_path"]
        with text_path.open() as f:
            text_email = f.read()
            text_email = text_email.replace("XXXXX", class_code)
            text_email = text_email.replace("YYYYY", student)
            text_part = MIMEText(text_email, "plain")

        # Note: the html one is what 99.99% of people will see, this is
        # how we add links, text formating, headings, etc to our emails.
        html_email = Path(__file__).parent / email_data["html_path"]
        with html_email.open() as f:
            html_email = f.read()
            html_email = html_email.replace("XXXXX", class_code)
            html_email = html_email.replace("YYYYY", student)
            html_part = MIMEText(html_email, "html")

        message = MIMEMultipart("alternative", _subparts=(text_part, html_part))
        message["Subject"] = email_data["subject"]
        message["From"] = self.account
        message["To"] = ",".join(recipients)

        return message

    def send_welcome_emails(self, recipients: list, student, class_code):
        email_data = {
            "subject": "Code 4 Tomorrow - XXXXX Acceptance",
            "text_path": "./emails/welcome.txt",
            "html_path": "./emails/welcome.html",
        }
        email_data["subject"] = email_data["subject"].replace("XXXXX", class_code)
        email = self.create_message(
            recipients,
            email_data,
            student,
            class_code,
        )
        self.send_email(email, recipients)

    def send_class_full_emails(self, recipients: list, student, class_code):
        email_data = {
            "subject": "Code 4 Tomorrow - XXXXX Class Full",
            "text_path": "./emails/class_full.txt",
            "html_path": "./emails/class_full.html",
        }
        email_data["subject"] = email_data["subject"].replace("XXXXX", class_code)
        email = self.create_message(
            recipients,
            email_data,
            student,
            class_code,
        )
        self.send_email(email, recipients)

    def send_invalid_code_emails(self, recipients: list, student, class_code):
        email_data = {
            "subject": "Code 4 Tomorrow - XXXXX Invalid Class Code",
            "text_path": "./emails/invalid_code.txt",
            "html_path": "./emails/invalid_code.html",
        }
        email_data["subject"] = email_data["subject"].replace("XXXXX", class_code)
        email = self.create_message(
            recipients,
            email_data,
            student,
            class_code,
        )
        self.send_email(email, recipients)
