import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from qrlib.QRComponent import QRComponent

# next oumk xbot yxyv
class EmailComponent(QRComponent):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        # Load credentials from vault.json manually
        vault_path = os.path.join(os.path.dirname(__file__), '..', 'devdata', 'vault.json')
        try:
            with open(vault_path, 'r') as vault_file:
                vault_data = json.load(vault_file)
                email_data = vault_data.get("email", {})
                self.sender_email = email_data.get("email_sender")
                self.sender_password = email_data.get("email_password")
                self.receiver_emails = email_data.get("email_receivers", [])
        except Exception as e:
            self.logger.error(f"Failed to load vault.json: {e}")
            raise ValueError("Could not load email credentials from vault.json")

        # Validate credentials
        if not self.sender_email or not self.sender_password:
            self.logger.error("Missing sender email or password in vault.json. Please ensure 'email.email_sender' and 'email.email_password' are set.")
            raise ValueError("Sender email credentials not found in vault")
        if not self.receiver_emails or not isinstance(self.receiver_emails, list):
            self.logger.error("Missing or invalid receiver emails in vault.json. Please ensure 'email.email_receivers' is a list of emails.")
            raise ValueError("Receiver emails not found or invalid in vault")

    def send_email_with_attachment(self, attachment_path, subject="Rotten Tomatoes Scraped Data", body="Attached is the scraped movie data from Rotten Tomatoes."):
        try:
            # Create the email
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(self.receiver_emails)  # Join list into comma-separated string
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach the file
            if os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(attachment_path)}",
                    )
                    msg.attach(part)
            else:
                self.logger.error(f"Attachment file not found: {attachment_path}")
                return

            # Send the email via Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                self.logger.info(f"Email sent successfully to {', '.join(self.receiver_emails)}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
