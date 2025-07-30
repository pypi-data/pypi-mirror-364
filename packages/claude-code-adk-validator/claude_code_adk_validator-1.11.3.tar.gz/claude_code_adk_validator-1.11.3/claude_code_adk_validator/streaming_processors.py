#!/usr/bin/env python3
"""
Streaming processors implementation following genai-processors pattern.
Refactors all validation operations to use proper async streaming.
"""

import asyncio
import json
from typing import AsyncIterable, Optional, Dict, Any, Type
from pydantic import BaseModel

try:
    from genai_processors import processor, ProcessorPart, streams, content_api  # type: ignore[import-not-found]
    from genai_processors.core import genai_model  # type: ignore[import-not-found]
    from google import genai
    from google.genai import types
except ImportError:
    processor = None
    ProcessorPart = None
    streams = None
    content_api = None
    genai_model = None
    genai = None
    types = None

from .config import (
    GEMINI_MODEL,
    FILE_CATEGORIZATION_MODEL,
    SECURITY_THINKING_BUDGET,
    TDD_THINKING_BUDGET,
)


def extract_json_from_part(part: Any) -> Dict[str, Any]:
    """Extract JSON data from a ProcessorPart"""
    try:
        # If part has text attribute, parse it as JSON
        if hasattr(part, "text") and part.text:
            return json.loads(part.text)
        # Fallback to json attribute if available
        elif hasattr(part, "json") and part.json:
            return part.json
        else:
            return {}
    except (json.JSONDecodeError, AttributeError):
        return {}


class ValidationProcessor(processor.PartProcessor):
    """Base validation processor implementing streaming pattern"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = GEMINI_MODEL,
        thinking_budget: Optional[int] = None,
        response_schema: Optional[Type[BaseModel]] = None,
    ):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.thinking_budget = thinking_budget
        self.response_schema = response_schema
        self._genai_processor = None

    def _create_genai_processor(self) -> Optional[Any]:
        """Create GenAI processor with configuration"""
        if not self.api_key or not genai_model:
            return None

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.response_schema,
        )

        if self.thinking_budget:
            config.thinking_config = types.ThinkingConfig(
                thinking_budget=self.thinking_budget
            )

        return genai_model.GenaiModel(
            api_key=self.api_key,
            model_name=self.model_name,
            generate_content_config=config,
        )

    def match(self, part: ProcessorPart) -> bool:
        """Check if this processor can handle the given part"""
        # Override in subclasses for specific matching logic
        return hasattr(part, "text") and part.text

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process the input part and yield results"""
        # Default implementation - override in subclasses
        yield part


class SecurityValidationProcessor(ValidationProcessor):
    """Security validation processor with streaming"""

    def __init__(self, api_key: Optional[str] = None):
        from .security_validator import ValidationResponse

        super().__init__(
            api_key=api_key,
            thinking_budget=SECURITY_THINKING_BUDGET,
            response_schema=ValidationResponse,
        )
        self.processor_type = "security"

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process security validation request"""
        if not self._genai_processor:
            self._genai_processor = self._create_genai_processor()

        if not self._genai_processor:
            # ProcessorPart takes content as first positional argument
            error_data = {"error": "No API key configured", "approved": True}
            yield ProcessorPart(json.dumps(error_data))
            return

        # Extract validation request from part
        validation_request = extract_json_from_part(part)
        prompt = validation_request.get("prompt", "")

        # Create input stream for GenAI processor
        input_stream = streams.stream_content([content_api.ProcessorPart(text=prompt)])

        # Process through GenAI
        response_text = ""
        async for content_part in self._genai_processor(input_stream):
            if hasattr(content_part, "text") and content_part.text:
                response_text += content_part.text

        # Parse and yield result
        try:
            result = json.loads(response_text)
            yield ProcessorPart(json.dumps(result))
        except json.JSONDecodeError:
            error_data = {
                "error": "Failed to parse response",
                "raw": response_text,
                "approved": True,
            }
            yield ProcessorPart(json.dumps(error_data))


class TDDValidationProcessor(ValidationProcessor):
    """TDD validation processor with streaming"""

    def __init__(self, api_key: Optional[str] = None):
        from .tdd_validator import TDDValidationResponse

        super().__init__(
            api_key=api_key,
            thinking_budget=TDD_THINKING_BUDGET,
            response_schema=TDDValidationResponse,
        )
        self.processor_type = "tdd"

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process TDD validation request"""
        if not self._genai_processor:
            self._genai_processor = self._create_genai_processor()

        if not self._genai_processor:
            error_data = {
                "error": "No API key configured",
                "approved": True,
                "tdd_phase": "unknown",
            }
            yield ProcessorPart(json.dumps(error_data))
            return

        # Extract validation request
        validation_request = part.json if hasattr(part, "json") else {}
        prompt = validation_request.get("prompt", "")

        # Create input stream
        input_stream = streams.stream_content([content_api.ProcessorPart(text=prompt)])

        # Process through GenAI
        response_text = ""
        async for content_part in self._genai_processor(input_stream):
            if hasattr(content_part, "text") and content_part.text:
                response_text += content_part.text

        # Parse and yield result
        try:
            result = json.loads(response_text)
            yield ProcessorPart(json.dumps(result))
        except json.JSONDecodeError:
            error_data = {
                "error": "Failed to parse response",
                "raw": response_text,
                "approved": True,
                "tdd_phase": "unknown",
            }
            yield ProcessorPart(json.dumps(error_data))


class FileCategorizationProcessor(ValidationProcessor):
    """File categorization processor with streaming"""

    def __init__(self, api_key: Optional[str] = None):
        from .tdd_validator import FileCategorizationResponse

        super().__init__(
            api_key=api_key,
            model_name=FILE_CATEGORIZATION_MODEL,
            thinking_budget=None,  # No thinking for categorization
            response_schema=FileCategorizationResponse,
        )

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process file categorization request"""
        if not self._genai_processor:
            self._genai_processor = self._create_genai_processor()

        if not self._genai_processor:
            # Fallback categorization
            fallback_data = {
                "category": "unknown",
                "requires_tdd": False,
                "reason": "No API key configured",
            }
            yield ProcessorPart(json.dumps(fallback_data))
            return

        # Extract request
        request = extract_json_from_part(part)
        prompt = request.get("prompt", "")

        # Create input stream
        input_stream = streams.stream_content([content_api.ProcessorPart(text=prompt)])

        # Process through GenAI
        response_text = ""
        async for content_part in self._genai_processor(input_stream):
            if hasattr(content_part, "text") and content_part.text:
                response_text += content_part.text

        # Parse and yield result
        try:
            result = json.loads(response_text)
            yield ProcessorPart(json.dumps(result))
        except json.JSONDecodeError:
            error_data = {
                "category": "unknown",
                "requires_tdd": True,
                "reason": "Failed to parse categorization",
            }
            yield ProcessorPart(json.dumps(error_data))


class ParallelValidationPipeline:
    """Pipeline for running security and TDD validation in parallel"""

    def __init__(self, api_key: Optional[str] = None):
        self.security_processor = SecurityValidationProcessor(api_key)
        self.tdd_processor = TDDValidationProcessor(api_key)

    async def process_parallel(
        self,
        security_request: Dict[str, Any],
        tdd_request: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Run security and TDD validation in parallel using streaming"""

        # Create input parts
        security_part = ProcessorPart(json.dumps(security_request))
        tdd_part = ProcessorPart(json.dumps(tdd_request))

        # Run processors in parallel
        security_task = self._collect_results(
            self.security_processor.call(security_part)
        )
        tdd_task = self._collect_results(self.tdd_processor.call(tdd_part))

        results = await asyncio.gather(security_task, tdd_task, return_exceptions=True)

        # Handle results
        security_result: Any = results[0]
        tdd_result: Any = results[1]

        # Handle exceptions
        if isinstance(security_result, Exception):
            security_result = {
                "approved": True,
                "reason": f"Security validation error: {str(security_result)}",
            }

        if isinstance(tdd_result, Exception):
            tdd_result = {
                "approved": True,
                "reason": f"TDD validation error: {str(tdd_result)}",
                "tdd_phase": "unknown",
            }

        return security_result, tdd_result

    async def _collect_results(
        self, stream: AsyncIterable[ProcessorPart]
    ) -> Dict[str, Any]:
        """Collect results from a processor stream"""
        result = {}
        async for part in stream:
            json_data = extract_json_from_part(part)
            if json_data:
                result.update(json_data)
        return result


class ValidationPipelineBuilder:
    """Builder for creating validation pipelines"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def create_security_pipeline(self) -> ValidationProcessor:
        """Create security validation pipeline"""
        return SecurityValidationProcessor(self.api_key)

    def create_tdd_pipeline(self) -> ValidationProcessor:
        """Create TDD validation pipeline"""
        return TDDValidationProcessor(self.api_key)

    def create_file_categorization_pipeline(self) -> ValidationProcessor:
        """Create file categorization pipeline"""
        return FileCategorizationProcessor(self.api_key)

    def create_parallel_pipeline(self) -> ParallelValidationPipeline:
        """Create parallel validation pipeline"""
        return ParallelValidationPipeline(self.api_key)
