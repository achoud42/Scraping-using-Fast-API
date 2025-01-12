import smtplib
from email.mime.text import MIMEText

class EmailNotification(NotificationStrategy):
    def __init__(self, smtp_server, port, username, password, recipient_email):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.recipient_email = recipient_email

    def notify(self, message: str):
        msg = MIMEText(message)
        msg['Subject'] = "Scraping Status"
        msg['From'] = self.username
        msg['To'] = self.recipient_email

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, self.recipient_email, msg.as_string())
