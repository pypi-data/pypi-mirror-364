"""Email address management for ARTL MCP.

This module provides utilities for managing email addresses required by various APIs,
with support for environment variables and validation to prevent bogus addresses.
"""

import os
import re
from pathlib import Path


class EmailManager:
    """Manages email addresses for API requests with validation support."""

    # Common bogus email patterns to reject
    BOGUS_PATTERNS = [
        r".*@example\.com$",
        r".*@test\.test$",
        r".*dummy.*@.*",
        r".*fake.*@.*",
        r".*placeholder.*@.*",
        r".*invalid.*@.*",
        r".*noreply.*@.*",
        r".*no-reply.*@.*",
    ]

    def __init__(self):
        """Initialize the email manager."""
        self._cached_email: str | None = None

    def get_email(self, provided_email: str | None = None) -> str | None:
        """Get a valid email address from various sources.

        Priority order:
        1. Provided email parameter (if valid)
        2. ARTL_EMAIL_ADDR environment variable
        3. local/.env file ARTL_EMAIL_ADDR value
        4. Return None if no valid email found

        Args:
            provided_email: Email address provided by caller

        Returns:
            Valid email address or None if none found

        Raises:
            ValueError: If provided_email is bogus/invalid
        """
        # Check provided email first
        if provided_email:
            if self._is_valid_email(provided_email):
                if self._is_bogus_email(provided_email):
                    raise ValueError(
                        f"Bogus email address not allowed: {provided_email}"
                    )
                return provided_email
            else:
                raise ValueError(f"Invalid email format: {provided_email}")

        # Use cached email if available
        if self._cached_email:
            return self._cached_email

        # Try environment variable
        env_email = os.getenv("ARTL_EMAIL_ADDR")
        if (
            env_email
            and self._is_valid_email(env_email)
            and not self._is_bogus_email(env_email)
        ):
            self._cached_email = env_email
            return env_email

        # Try local/.env file
        env_file_email = self._read_env_file()
        if (
            env_file_email
            and self._is_valid_email(env_file_email)
            and not self._is_bogus_email(env_file_email)
        ):
            self._cached_email = env_file_email
            return env_file_email

        return None

    def require_email(self, provided_email: str | None = None) -> str:
        """Get a valid email address, raising an error if none found.

        Args:
            provided_email: Email address provided by caller

        Returns:
            Valid email address

        Raises:
            ValueError: If no valid email found or email is bogus
        """
        email = self.get_email(provided_email)
        if not email:
            raise ValueError(
                "No valid email address found. Please:\n"
                "1. Set ARTL_EMAIL_ADDR environment variable, or\n"
                "2. Add ARTL_EMAIL_ADDR=your@email.com to local/.env file, or\n"
                "3. Provide --email parameter to CLI commands"
            )
        return email

    def _is_valid_email(self, email: str) -> bool:
        """Check if email has valid format."""
        if not email or not isinstance(email, str):
            return False
        pattern = r"^(?!.*\.\.)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return (
            bool(re.match(pattern, email))
            and not email.startswith(".")
            and not email.endswith(".")
        )

    def _is_bogus_email(self, email: str) -> bool:
        """Check if email matches bogus patterns."""
        for pattern in self.BOGUS_PATTERNS:
            if re.match(pattern, email, re.IGNORECASE):
                return True
        return False

    def _read_env_file(self) -> str | None:
        """Read email from local/.env file."""
        env_file = Path("local/.env")
        if not env_file.exists():
            return None

        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ARTL_EMAIL_ADDR="):
                        return line.split("=", 1)[1].strip()
                    # Also support legacy email_address format
                    elif line.startswith("email_address="):
                        return line.split("=", 1)[1].strip()
        except Exception:
            return None

        return None

    def validate_for_api(self, api_name: str, email: str | None = None) -> str:
        """Validate email for specific API usage.

        Args:
            api_name: Name of the API requiring email
            email: Optional email to validate

        Returns:
            Valid email address

        Raises:
            ValueError: If no valid email or API-specific requirements not met
        """
        # If email is provided directly, validate it without using require_email
        if email:
            if not self._is_valid_email(email):
                raise ValueError(f"Invalid email format: {email}")
            if self._is_bogus_email(email):
                raise ValueError(
                    f"{api_name} API requires a real institutional email address"
                )
            return email

        # Otherwise use require_email for environment/file email
        validated_email = self.require_email()

        # API-specific validation
        if api_name.lower() in ["unpaywall", "crossref"]:
            # These APIs prefer institutional emails
            if validated_email.endswith("@example.com"):
                raise ValueError(
                    f"{api_name} API requires a real institutional email address"
                )

        return validated_email


# Global instance for convenience
email_manager = EmailManager()


def get_email(provided_email: str | None = None) -> str | None:
    """Convenience function to get email address."""
    return email_manager.get_email(provided_email)


def require_email(provided_email: str | None = None) -> str:
    """Convenience function to require email address."""
    return email_manager.require_email(provided_email)
