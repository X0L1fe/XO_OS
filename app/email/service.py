import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from jinja2 import Template

from app.config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Сервис для отправки писем по SMTP.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        # Set up Jinja2 environment for template loading
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")

    def _render_template(self, template_name: str, **context) -> str:
        """
        Render a Jinja2 template with the given context.

        Args:
            template_name: Name of the template file (e.g., "verification_email.html")
            **context: Variables to pass to the template

        Returns:
            Rendered HTML string
        """
        template_path = os.path.join(self.template_dir, template_name)

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        return template.render(**context)

    def send_verification_email(
        self, email: str, verification_token: str, frontend_url: str
    ) -> None:
        """
        Отправьте электронное письмо с подтверждением регистрации.

        Args:
            email: адрес электронной почты получателя
            verification_token: токен проверки, который нужно включить в ссылку.
            frontend_url: базовый URL-адрес внешнего интерфейса для создания проверочной ссылки.
        """
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning(
                "Email not configured. Skipping email sending for verification."
            )
            logger.info(
                f"Would send verification email to {email} with token {verification_token}"
            )
            return

        try:
            # Create verification URL
            verify_url = (
                f"{frontend_url.rstrip('/')}/verify-email?token={verification_token}"
            )

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Подтверждение электронной почты для XO_OS"
            msg["From"] = self.settings.smtp_from_email
            msg["To"] = email

            # Render HTML template
            html_content = self._render_template(
                "verification_email.html",
                FRONTEND_URL=frontend_url,
                VERIFICATION_TOKEN=verification_token,
            )

            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port
            ) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    server.login(
                        self.settings.smtp_username, self.settings.smtp_password
                    )
                server.send_message(msg)

            logger.info(f"Verification email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            # In development, we might want to raise this, but for now we'll just log
            # to not break the registration flow if email fails
            raise

    def send_password_reset_email(
        self, email: str, reset_token: str, frontend_url: str
    ) -> None:
        """
        Отправьте электронное письмо для сброса пароля.

        Args:
            email: адрес электронной почты получателя
            reset_token: токен для сброса пароля
            frontend_url: базовый URL-адрес внешнего интерфейса
        """
        # If email is not configured, just log and don't fail
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning(
                "Email not configured. Skipping email sending for password reset."
            )
            logger.info(
                f"Would send password reset email to {email} with token {reset_token}"
            )
            return

        try:
            # Create reset URL
            reset_url = f"{frontend_url.rstrip('/')}/reset-password?token={reset_token}"

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Сброс пароля для XO_OS"
            msg["From"] = self.settings.smtp_from_email
            msg["To"] = email

            # Render HTML template
            html_content = self._render_template(
                "password_reset.html",
                FRONTEND_URL=frontend_url,
                RESET_TOKEN=reset_token,
            )

            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port
            ) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    server.login(
                        self.settings.smtp_username, self.settings.smtp_password
                    )
                server.send_message(msg)

            logger.info(f"Password reset email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            # In development, we might want to raise this, but for now we'll just log
            # to not break the flow if email fails
            raise

    def send_email_change_intent_email(
        self,
        email: str,
        email_change_token: str,
        frontend_url: str,
        current_email: str,
        new_email: str,
    ) -> None:
        """
        Отправьте электронное письмо с запросом подтверждения смены email.

        Args:
            email: адрес электронной почты получателя (текущий email)
            email_change_token: токен для подтверждения смены email
            frontend_url: базовый URL-адрес внешнего интерфейса
            current_email: текущий email пользователя
            new_email: новый email, на который пользователь хочет поменять
        """
        # If email is not configured, just log and don't fail
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning(
                "Email not configured. Skipping email sending for email change intent."
            )
            logger.info(
                f"Would send email change intent email to {email} with token {email_change_token}"
            )
            return

        try:
            # Create confirmation URL
            confirm_url = (
                f"{frontend_url.rstrip('/')}/change-email?token={email_change_token}"
            )

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Подтверждение смены email для XO_OS"
            msg["From"] = self.settings.smtp_from_email
            msg["To"] = email

            # Render HTML template
            html_content = self._render_template(
                "email_change_intent.html",
                FRONTEND_URL=frontend_url,
                EMAIL_CHANGE_INTENT_TOKEN=email_change_token,
                CURRENT_EMAIL=current_email,
                NEW_EMAIL=new_email,
            )

            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port
            ) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    server.login(
                        self.settings.smtp_username, self.settings.smtp_password
                    )
                server.send_message(msg)

            logger.info(f"Email change intent email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send email change intent email to {email}: {e}")
            # In development, we might want to raise this, but for now we'll just log
            # to not break the flow if email fails
            raise

    def send_email_change_confirmation_email(
        self,
        email: str,
        email_change_confirmation_token: str,
        frontend_url: str,
        new_email: str,
    ) -> None:
        """
        Отправьте электронное письмо с подтверждением новой электронной почты.

        Args:
            email: адрес электронной почты получателя (новый email)
            email_change_confirmation_token: токен для подтверждения нового email
            frontend_url: базовый URL-адрес внешнего интерфейса
            new_email: новый email пользователя
        """
        # If email is not configured, just log and don't fail
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning(
                "Email not configured. Skipping email sending for email change confirmation."
            )
            logger.info(
                f"Would send email change confirmation email to {email} with token {email_change_confirmation_token}"
            )
            return

        try:
            # Create confirmation URL
            confirm_url = f"{frontend_url.rstrip('/')}/confirm-new-email?token={email_change_confirmation_token}"

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Подтверждение нового email — XO_OS"
            msg["From"] = self.settings.smtp_from_email
            msg["To"] = email

            # Render HTML template
            html_content = self._render_template(
                "email_change_confirmation.html",
                FRONTEND_URL=frontend_url,
                EMAIL_CHANGE_CONFIRMATION_TOKEN=email_change_confirmation_token,
                NEW_EMAIL=new_email,
            )

            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(
                self.settings.smtp_host, self.settings.smtp_port
            ) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()
                if self.settings.smtp_username and self.settings.smtp_password:
                    server.login(
                        self.settings.smtp_username, self.settings.smtp_password
                    )
                server.send_message(msg)

            logger.info(f"Email change confirmation email sent to {email}")

        except Exception as e:
            logger.error(
                f"Failed to send email change confirmation email to {email}: {e}"
            )
            # In development, we might want to raise this, but for now we'll just log
            # to not break the flow if email fails
            raise
