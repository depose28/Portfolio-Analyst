"""
Email Sender Module - Sends digest emails via Gmail SMTP
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending digest emails via Gmail SMTP"""

    def __init__(
        self,
        smtp_email: str,
        smtp_password: str,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587
    ):
        """
        Initialize email sender

        Args:
            smtp_email: Gmail address to send from
            smtp_password: Gmail App Password (not regular password)
            smtp_host: SMTP server host
            smtp_port: SMTP server port
        """
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_digest(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        recipient_name: Optional[str] = None
    ) -> bool:
        """
        Send a digest email

        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            body: Email body (plain text)
            recipient_name: Optional recipient name

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_email
            message["To"] = recipient_email

            # Add body
            text_part = MIMEText(body, "plain")
            message.attach(text_part)

            # Connect to SMTP server and send
            logger.info(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.smtp_email, self.smtp_password)

                logger.info(f"Sending email to: {recipient_email}")
                server.send_message(message)

            logger.info("Email sent successfully!")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            logger.error("Make sure you're using a Gmail App Password, not your regular password")
            logger.error("See: https://support.google.com/accounts/answer/185833")
            return False

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_test_email(self, recipient_email: str) -> bool:
        """
        Send a test email to verify configuration

        Args:
            recipient_email: Email address to send test to

        Returns:
            True if test email sent successfully
        """
        subject = "Portfolio Monitor - Test Email"
        body = """
This is a test email from your Portfolio Monitor.

If you're receiving this, your email configuration is working correctly!

You should start receiving weekly portfolio digests on Monday mornings.

---
Portfolio Monitor
        """.strip()

        logger.info("Sending test email...")
        return self.send_digest(recipient_email, subject, body)
