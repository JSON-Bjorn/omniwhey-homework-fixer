import re
import uuid
from typing import Any, Union


def censor_email(email: str) -> str:
    """
    Censor an email address to show only first character and domain.

    Args:
        email: The email to censor

    Returns:
        Censored email string

    Example:
        'user@example.com' -> 'u****@example.com'
    """
    if not email or "@" not in email:
        return "[invalid-email]"

    username, domain = email.split("@", 1)
    if not username:
        return f"@{domain}"

    censored_username = username[0] + "*" * (len(username) - 1)
    return f"{censored_username}@{domain}"


def censor_uuid(uuid_val: Union[uuid.UUID, str]) -> str:
    """
    Censor a UUID to show only first and last 4 characters.

    Args:
        uuid_val: UUID value to censor

    Returns:
        Censored UUID string

    Example:
        '123e4567-e89b-12d3-a456-426614174000' -> '123e...4000'
    """
    if not uuid_val:
        return "[invalid-uuid]"

    uuid_str = str(uuid_val)
    if len(uuid_str) < 8:  # Too short to be a real UUID
        return "[invalid-uuid]"

    return f"{uuid_str[:4]}...{uuid_str[-4:]}"


def censor_token(token: str) -> str:
    """
    Censor an authentication token to show only first and last 4 characters.

    Args:
        token: Authentication token to censor

    Returns:
        Censored token string

    Example:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' -> 'eyJh...xxx'
    """
    if not token:
        return "[invalid-token]"

    if len(token) < 8:
        return "[token-too-short]"

    return f"{token[:4]}...{token[-3:]}"


def censor_name(name: str) -> str:
    """
    Censor a personal name to show only first character of each name part.

    Args:
        name: The name to censor

    Returns:
        Censored name string

    Example:
        'John Smith' -> 'J. S.'
    """
    if not name:
        return "[invalid-name]"

    parts = name.strip().split()
    censored_parts = [f"{part[0]}." if part else "" for part in parts]
    return " ".join(censored_parts)


def censor_ip_address(ip: str) -> str:
    """
    Censor an IP address to hide part of it.

    Args:
        ip: IP address to censor

    Returns:
        Censored IP address

    Example:
        '192.168.1.1' -> '192.168.x.x'
        '2001:0db8:85a3:0000:0000:8a2e:0370:7334' -> '2001:0db8:x:x:x:x:x:x'
    """
    if not ip:
        return "[invalid-ip]"

    # IPv4
    ipv4_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    if re.match(ipv4_pattern, ip):
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.x.x"
        return "[malformed-ipv4]"

    # IPv6
    ipv6_pattern = r"[0-9a-fA-F:]{4,}"
    if re.match(ipv6_pattern, ip):
        parts = ip.split(":")
        if len(parts) > 2:
            return f"{parts[0]}:{parts[1]}:" + ":".join(
                ["x"] * (len(parts) - 2)
            )
        return "[malformed-ipv6]"

    return "[unknown-ip-format]"


def censor_password(password: str) -> str:
    """
    Completely censor a password.

    Args:
        password: Password to censor

    Returns:
        Censored password string
    """
    if not password:
        return "[empty-password]"
    return "[REDACTED]"


def censor_sensitive_data(log_text: str) -> str:
    """
    Censor potentially sensitive data in a log message.

    Args:
        log_text: The log text to censor

    Returns:
        Censored log text
    """
    # Pattern for common sensitive data in logs
    patterns = {
        # Email pattern
        r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)": lambda m: censor_email(
            m.group(1)
        ),
        # UUID pattern
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})": lambda m: censor_uuid(
            m.group(1)
        ),
        # Authorization header pattern
        r"(Authorization: Bearer\s+)([^\s]+)": lambda m: f"{m.group(1)}{censor_token(m.group(2))}",
        # Token without context
        r"(token\s*[=:]\s*)([^\s,;]+)": lambda m: f"{m.group(1)}{censor_token(m.group(2))}",
        # IP address patterns
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})": lambda m: censor_ip_address(
            m.group(1)
        ),
    }

    result = log_text
    for pattern, replacement_func in patterns.items():
        result = re.sub(pattern, replacement_func, result)

    return result


def get_secure_logger_message(
    message: str, sensitive_data: bool = True
) -> str:
    """
    Prepare a message for secure logging.

    Args:
        message: The log message
        sensitive_data: Whether message might contain sensitive data

    Returns:
        Securely formatted log message
    """
    if sensitive_data:
        return censor_sensitive_data(message)
    return message
