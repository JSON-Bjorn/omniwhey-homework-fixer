from typing import List, Dict, Any, Optional
import logging
from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
    MessageType,
)
from pydantic import EmailStr

from app.core.config import settings

# Set up logger
logger = logging.getLogger(__name__)

# Configure FastAPI Mail
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(
    email_to: List[EmailStr],
    subject: str,
    body: str,
    template_name: Optional[str] = None,
    template_body: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Send an email using FastAPI Mail.

    Args:
        email_to: List of recipient email addresses
        subject: Email subject
        body: Plain text email body
        template_name: Optional HTML template name
        template_body: Optional template context variables

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Check if email settings are configured
    if not all(
        [
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD,
            settings.MAIL_FROM,
            settings.MAIL_SERVER,
        ]
    ):
        logger.warning("Email settings not configured. Email not sent.")
        return False

    try:
        # Create FastAPI mail client
        fastmail = FastMail(mail_config)

        # Create message
        if template_name and template_body:
            # Use HTML template
            message = MessageSchema(
                subject=subject,
                recipients=email_to,
                template_body=template_body,
                subtype=MessageType.html,
            )

            # Send email with template
            await fastmail.send_message(message, template_name=template_name)
        else:
            # Plain text message
            message = MessageSchema(
                subject=subject,
                recipients=email_to,
                body=body,
                subtype=MessageType.plain,
            )

            # Send email
            await fastmail.send_message(message)

        logger.info(f"Email sent to {', '.join(email_to)}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


async def send_verification_email(
    email_to: EmailStr, verification_link: str, user_name: str
) -> bool:
    """
    Send a verification email to a new user.

    Args:
        email_to: Recipient email address
        verification_link: Email verification link
        user_name: User's name

    Returns:
        True if email was sent successfully, False otherwise
    """
    subject = f"{settings.PROJECT_NAME} - Verify your email address"

    # Plain text version as fallback
    text_content = f"""
    Hello {user_name},
    
    Thank you for registering with {settings.PROJECT_NAME}!
    
    Please verify your email address by clicking the link below:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you did not register for an account, please ignore this email.
    
    Regards,
    The {settings.PROJECT_NAME} Team
    """

    # HTML template context
    template_body = {
        "user_name": user_name,
        "verification_link": verification_link,
        "project_name": settings.PROJECT_NAME,
    }

    try:
        # Send email with HTML template
        result = await send_email(
            email_to=[email_to],
            subject=subject,
            body=text_content,
            template_name="email_verification.html",
            template_body=template_body,
        )

        if result:
            logger.info(f"Verification email sent to {email_to}")
        else:
            logger.warning(f"Verification email not sent to {email_to}")

        return result

    except Exception as e:
        logger.error(
            f"Error sending verification email to {email_to}: {str(e)}"
        )
        return False
