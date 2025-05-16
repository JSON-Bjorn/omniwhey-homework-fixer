"""
AI services for OpenAI and Anthropic integration.
"""

from typing import Optional, Dict, Any
import re
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)

from openai import OpenAI, APIConnectionError as OpenAIAPIConnectionError
from anthropic import Anthropic, APIError as AnthropicAPIError

from app.core.config import settings
from app.ai.prompts import (
    GENERATE_CORRECTION_TEMPLATE_PROMPT,
    GRADE_ASSIGNMENT_PROMPT,
    SIMPLE_GRADE_ASSIGNMENT_PROMPT,
)

logger = logging.getLogger(__name__)


def create_client_without_proxies(client_class, **kwargs):
    """
    Create an API client without passing any problematic parameters.

    Args:
        client_class: The client class to instantiate (OpenAI or Anthropic)
        **kwargs: Arguments to pass to the client constructor

    Returns:
        Instantiated API client with filtered parameters
    """
    # Filter out known problematic parameters
    if "proxies" in kwargs:
        logger.debug(
            f"Filtering out 'proxies' parameter from {client_class.__name__} initialization"
        )
        del kwargs["proxies"]

    # Additional safety check - filter out any kwargs that aren't accepted by the constructor
    try:
        import inspect

        valid_params = set(
            inspect.signature(client_class.__init__).parameters.keys()
        )
        # Filter out self (always the first parameter)
        if "self" in valid_params:
            valid_params.remove("self")

        # Filter out parameters that aren't in the signature
        for param in list(kwargs.keys()):
            if param not in valid_params:
                logger.debug(
                    f"Filtering out unexpected parameter '{param}' from {client_class.__name__} initialization"
                )
                del kwargs[param]
    except Exception as e:
        logger.warning(
            f"Could not inspect {client_class.__name__} signature: {e}"
        )

    return client_class(**kwargs)


class AIService:
    """Service for interacting with AI APIs."""

    def __init__(self):
        """Initialize AI clients."""
        self.openai_client = self._setup_openai()
        self.anthropic_client = self._setup_anthropic()

    def _setup_openai(self) -> Optional[OpenAI]:
        """Set up OpenAI client if API key is available."""
        if settings.OPENAI_API_KEY:
            try:
                # Use wrapper function to filter out problematic parameters
                return create_client_without_proxies(
                    OpenAI, api_key=settings.OPENAI_API_KEY
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                return None
        return None

    def _setup_anthropic(self) -> Optional[Anthropic]:
        """Set up Anthropic client if API key is available."""
        if settings.ANTHROPIC_API_KEY:
            try:
                # Use wrapper function to filter out problematic parameters
                return create_client_without_proxies(
                    Anthropic, api_key=settings.ANTHROPIC_API_KEY
                )
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                return None
        return None

    @retry(
        retry=retry_if_exception_type(
            (OpenAIAPIConnectionError, AnthropicAPIError)
        ),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
    )
    async def generate_correction_template(
        self, assignment_instructions: str, max_score: int
    ) -> str:
        """
        Generate a correction template using OpenAI.

        Args:
            assignment_instructions: The assignment instructions text
            max_score: Maximum score for the assignment

        Returns:
            Generated correction template

        Raises:
            Exception: If API calls fail
        """
        prompt = GENERATE_CORRECTION_TEMPLATE_PROMPT.format(
            assignment_instructions=assignment_instructions,
            max_score=max_score,
        )

        # Try OpenAI first
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")

        # Fall back to Anthropic if OpenAI fails or is not available
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                )
                return response.content[0].text or ""
            except Exception as e:
                logger.error(f"Anthropic API error: {str(e)}")

        # If both services fail
        raise Exception(
            "All AI services failed to generate a correction template"
        )

    @retry(
        retry=retry_if_exception_type(
            (OpenAIAPIConnectionError, AnthropicAPIError)
        ),
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
    )
    async def grade_assignment(
        self,
        assignment_instructions: str,
        student_submission: str,
        max_score: int,
        correction_template: Optional[str] = None,
    ) -> int:
        """
        Grade a student assignment using Anthropic (with fallback to OpenAI).

        Args:
            assignment_instructions: The assignment instructions text
            student_submission: The student's submission text
            max_score: Maximum score for the assignment
            correction_template: Correction template (if available)

        Returns:
            Assignment score as an integer

        Raises:
            Exception: If API calls fail or score cannot be parsed
        """
        # Prepare prompt based on whether correction template is available
        if correction_template:
            prompt = GRADE_ASSIGNMENT_PROMPT.format(
                assignment_instructions=assignment_instructions,
                correction_template=correction_template,
                student_submission=student_submission,
                max_score=max_score,
            )
        else:
            prompt = SIMPLE_GRADE_ASSIGNMENT_PROMPT.format(
                assignment_instructions=assignment_instructions,
                student_submission=student_submission,
                max_score=max_score,
            )

        # Try Anthropic first for grading (as per requirements)
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=10,  # Limit tokens since we want just the score
                    temperature=0.2,  # Lower temperature for more consistent results
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                )
                raw_score = (
                    response.content[0].text.strip()
                    if response.content
                    else ""
                )
                return self._parse_score(raw_score, max_score)
            except Exception as e:
                logger.error(f"Anthropic API error: {str(e)}")

        # Fall back to OpenAI if Anthropic fails or is not available
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_tokens=10,  # Limit tokens since we want just the score
                )
                raw_score = (
                    response.choices[0].message.content.strip()
                    if response.choices
                    else ""
                )
                return self._parse_score(raw_score, max_score)
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")

        # If both services fail
        raise Exception("All AI services failed to grade the assignment")

    def _parse_score(self, raw_score: str, max_score: int) -> int:
        """
        Parse and validate the score from AI response.

        Args:
            raw_score: The raw score text from API
            max_score: Maximum allowed score

        Returns:
            Validated score as integer

        Raises:
            ValueError: If score cannot be parsed or is invalid
        """
        # Extract numbers from the response
        numbers = re.findall(r"\d+", raw_score)

        if not numbers:
            raise ValueError(
                f"No numeric score found in response: '{raw_score}'"
            )

        # Take the first number found
        score = int(numbers[0])

        # Validate the score
        if score < 0:
            logger.warning(f"Negative score found: {score}, setting to 0")
            return 0
        if score > max_score:
            logger.warning(
                f"Score {score} exceeds maximum {max_score}, capping at max"
            )
            return max_score

        return score


# Create a single instance of the AI service
ai_service = AIService()
