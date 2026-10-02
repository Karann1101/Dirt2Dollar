import re
from typing import Optional

from src.base.base_service import BaseService
from src.domain.entities.workflow_context import WorkflowContext
from src.providers.llm.groq_provider import GroqProvider
from src.prompts.client_name_extraction_prompt import (
    CLIENT_NAME_EXTRACTION_SYSTEM_PROMPT,
)
from src.core.exceptions import ValidationException
from src.core.logging import logger


# Words that signal the query is an instruction/sentence rather than a
# bare client name (e.g. "give me churn analysis for X" vs just "X").
# If any of these appear, we do NOT treat the whole query as a name.
_INSTRUCTION_WORDS = {
    "give", "show", "tell", "what", "how", "please", "need",
    "want", "get", "find", "fetch", "pull", "run", "generate",
    "analyze", "analyse", "is", "are", "does", "do", "can",
    "could", "would", "should", "report", "summary", "analysis",
    "churn", "kpi", "update", "updates", "status", "?",
}


class ClientNameExtractionNode(BaseService):
    """
    Service to extract client name from user query.

    Flow:
    1. Try code-based extraction first (including a bare-name fallback).
    2. If it fails, use LLM fallback.
    3. Store final result in context.client_name.
    """

    def __init__(self):
        # Initialize base service
        super().__init__(
            service_name="Client Name Extraction Service",
            service_type="CLIENT_NAME_EXTRACTION"
        )

        # Initialize Groq provider for AI fallback
        self.groq_provider = GroqProvider()

    def validate(self, context: WorkflowContext):
        """
        Validate that user_query exists in context metadata.
        """
        user_query = context.metadata.get("user_query")

        if not user_query:
            raise ValidationException(
                "user_query is required inside context.metadata"
            )

        return True

    def _clean_extracted_name(
        self,
        extracted_name: str
    ) -> str:
        """
        Clean unwanted trailing words from extracted client name.
        """
        extracted_name = extracted_name.strip(" .,!?:")

        trailing_words_pattern = (
            r"\b(in|on|at|with|for|from|this|that|full|details|latest)\b.*$"
        )

        extracted_name = re.sub(
            trailing_words_pattern,
            "",
            extracted_name,
            flags=re.IGNORECASE
        ).strip()

        return extracted_name

    def _looks_like_bare_name(
        self,
        user_query: str
    ) -> bool:
        """
        True if the query looks like just a client name typed on its own
        (e.g. "Yardworx Land Management") rather than a sentence/instruction
        (e.g. "give me churn analysis for Yardworx Land Management").
        """
        stripped = user_query.strip(" .,!?:")

        if not stripped:
            return False

        # Must look like a plausible name: letters, digits, spaces, and a
        # small set of punctuation common in business names.
        if not re.fullmatch(r"[a-zA-Z0-9&'.\-\s]+", stripped):
            return False

        words = stripped.split()

        # A bare name is short. Long strings are more likely a sentence.
        if len(words) == 0 or len(words) > 6:
            return False

        # If any word matches a known instruction/question word, this is
        # a sentence, not a bare name.
        lowered_words = {w.lower().strip(".,!?") for w in words}
        if lowered_words & _INSTRUCTION_WORDS:
            return False

        return True

    def _extract_client_name_code(
        self,
        user_query: str
    ) -> Optional[str]:
        """
        Try to extract client name using regex-based logic.
        Works for both lowercase and uppercase queries.
        """
        try:
            patterns = [
                r"(?:for|of|about)\s+([a-zA-Z][a-zA-Z0-9&'_.-]*(?:\s+[a-zA-Z][a-zA-Z0-9&'_.-]*)*)",
                r"client\s+([a-zA-Z][a-zA-Z0-9&'_.-]*(?:\s+[a-zA-Z][a-zA-Z0-9&'_.-]*)*)",
                r"([a-zA-Z][a-zA-Z0-9&'_.-]*(?:\s+[a-zA-Z][a-zA-Z0-9&'_.-]*)*)\s+(?:report|summary|analysis|churn|kpi|updates)",
            ]

            for pattern in patterns:
                match = re.search(
                    pattern,
                    user_query,
                    flags=re.IGNORECASE
                )

                if match:
                    extracted_name = match.group(1).strip()
                    extracted_name = self._clean_extracted_name(
                        extracted_name
                    )

                    if extracted_name:
                        return extracted_name

            # Fallback: no instruction pattern matched. If the whole query
            # looks like a bare client name typed on its own (e.g. just
            # "Yardworx Land Management" with no surrounding sentence),
            # treat the entire query as the client name. This makes a
            # plain name input behave identically to a full instruction
            # sentence containing the same name, without needing an LLM
            # round-trip for the common case.
            if self._looks_like_bare_name(user_query):
                return user_query.strip(" .,!?:")

            return None

        except re.error as error:
            # A malformed regex would be a programming bug, not
            # a user-facing failure — log it and fall through to AI extraction.
            logger.error(f"Regex extraction failed unexpectedly: {error}")
            return None

    def _extract_client_name_ai(
        self,
        user_query: str
    ) -> Optional[str]:
        """
        Use AI fallback to extract the client name.
        If Groq fails, return None instead of crashing.
        """

        prompt = f"""
Extract the client name from the following user query.

User Query:
{user_query}

Return only the client name.
If no client name is found, return UNKNOWN.
""".strip()

        try:
            response = self.groq_provider.generate_response(
                prompt=prompt,
                system_prompt=CLIENT_NAME_EXTRACTION_SYSTEM_PROMPT,
                temperature=0.0,
                max_tokens=100,
                reasoning_format="hidden",
            )

            content = response.get("content", "").strip()

            if not content or content.upper() == "UNKNOWN":
                return None

            # Reasoning-capable models can still leak a sentence of
            # internal explanation even with reasoning_format="hidden"
            # (e.g. "The client name is Acme Corp"), rather than a bare
            # name. If the response looks like a sentence rather than a
            # name, discard it rather than trusting it verbatim, so a
            # leaked explanation doesn't get passed on as if it were the
            # client name.
            if len(content.split()) > 8 or content.endswith('.') or '"' in content:
                logger.warning(
                    f"AI client-name extraction returned a sentence instead of "
                    f"a bare name, discarding: {content!r}"
                )
                return None

            return content

        except Exception as error:
            # Intentionally non-fatal: this is a fallback path.
            # If AI extraction fails, the node simply reports "not_found"
            # rather than crashing the whole workflow.
            logger.warning(f"AI fallback for client name extraction failed: {error}")
            return None

    def process(
        self,
        context: WorkflowContext
    ) -> WorkflowContext:
        """
        Main processing logic:
        first code-based extraction,
        then AI fallback if needed.
        """

        user_query = context.metadata.get("user_query", "").strip()

        # Step 1: Try code-based extraction
        extracted_name = self._extract_client_name_code(
            user_query
        )

        if extracted_name:
            context.client_name = extracted_name
            context.metadata["client_name_extraction_method"] = "code"
            return context

        # Step 2: Try AI fallback
        extracted_name = self._extract_client_name_ai(
            user_query
        )

        if extracted_name:
            context.client_name = extracted_name
            context.metadata["client_name_extraction_method"] = "ai"
        else:
            context.client_name = None
            context.metadata["client_name_extraction_method"] = "not_found"

        return context


if __name__ == "__main__":
    user_query = input("Enter user query: ").strip()

    context = WorkflowContext()
    context.metadata["user_query"] = user_query

    service = ClientNameExtractionNode()

    try:
        result = service.execute(context)
        print("\nExtracted Client Name:", result.client_name)
        print(
            "Extraction Method:",
            result.metadata.get("client_name_extraction_method")
        )
    except Exception as error:
        print(f"Extraction failed: {error}")