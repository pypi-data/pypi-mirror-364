import logging

from openai import AsyncOpenAI

from fraudcrawler.base.base import Prompt
from fraudcrawler.settings import (
    PROCESSOR_USER_PROMPT_TEMPLATE,
    PROCESSOR_DEFAULT_IF_MISSING,
)


logger = logging.getLogger(__name__)


class Processor:
    """Processes product data for classification based on a prompt configuration."""

    def __init__(
        self,
        api_key: str,
        model: str,
        default_if_missing: int = PROCESSOR_DEFAULT_IF_MISSING,
    ):
        """Initializes the Processor.

        Args:
            api_key: The OpenAI API key.
            model: The OpenAI model to use.
            default_if_missing: The default classification to return if error occurs.
        """
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._default_if_missing = default_if_missing

    async def _call_openai_api(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        """Calls the OpenAI API with the given user prompt."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI API")
        return content

    async def classify(self, prompt: Prompt, url: str, product_details: str) -> int:
        """A generic classification method that classifies a product based on a prompt object.

        Args:
            prompt: A dictionary with keys "system_prompt", etc.
            url: Product URL (often used in the user_prompt).
            product_details: String with product details, formatted per prompt.product_item_fields.

        Note:
            This method returns `PROCESSOR_DEFAULT_IF_MISSING` if:
                - product_details is empty
                - an error occurs during the API call
                - if the response isn't in allowed_classes.
        """
        # If required fields are missing, return the prompt's default fallback if provided.
        if not product_details:
            logger.warning("Missing required product_details for classification.")
            return self._default_if_missing

        # Substitute placeholders in user_prompt with the relevant arguments
        user_prompt = PROCESSOR_USER_PROMPT_TEMPLATE.format(
            product_details=product_details,
        )

        # Call the OpenAI API
        try:
            logger.debug(
                f'Calling OpenAI API for classification (url="{url}", prompt="{prompt.name}")'
            )
            content = await self._call_openai_api(
                system_prompt=prompt.system_prompt,
                user_prompt=user_prompt,
                max_tokens=1,
            )
            classification = int(content.strip())

            # Enforce that the classification is in the allowed classes
            if classification not in prompt.allowed_classes:
                logger.warning(
                    f"Classification '{classification}' not in allowed classes {prompt.allowed_classes}"
                )
                return self._default_if_missing

            logger.info(
                f'Classification for url="{url}" (prompt={prompt.name}): {classification}'
            )
            return classification

        except Exception as e:
            logger.error(
                f'Error classifying product at url="{url}" with prompt "{prompt.name}": {e}'
            )
            return self._default_if_missing
