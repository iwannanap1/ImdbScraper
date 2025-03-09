from qrlib.QRComponent import QRComponent
import logging
from qrlib.QREnv import QREnv
from RPA.Email.ImapSmtp import ImapSmtp

class EmailComponent(QRComponent):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("EmailComponent")
        self.attachment_path = "C:\\Users\\Shrijana\\Downloads\\bot-starter-kit-v2.0\\bot-starter-kit-v2.0\\movies_data.xlsx"
        self.subject = "IMDB"
        self.sender_email = None
        self.sender_password = None
        self.receiver_emails = None

    def get_vault_data(self):
        email = QREnv.VAULTS["email"]
        self.sender_email = email["email_sender"]
        self.sender_password = email["email_password"]
        self.receiver_emails = email["email_receivers"]
        self.logger.info(f"Loaded Email Config: {self.sender_email}, Receivers: {self.receiver_emails}")

    def send_email_with_attachment(self):
        self.get_vault_data() 
        self.logger.info(f"Attachment path: {self.attachment_path}")
        mail = ImapSmtp(smtp_server="smtp.gmail.com", smtp_port=587)
        mail.authorize(account=self.sender_email, password=self.sender_password)
        mail.send_message(
            sender=self.sender_email,
            recipients=self.receiver_emails,
            subject=self.subject,
            body = "IMDB scrapper",
            attachments=[self.attachment_path]
        )
