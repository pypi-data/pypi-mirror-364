#!/usr/bin/env python3
"""Test suite for streaming processors to ensure basic functionality."""

import asyncio
import json
import pytest
from typing import AsyncIterable

# Skip tests if genai_processors not available
pytest.importorskip("genai_processors")

from genai_processors import processor, ProcessorPart, streams

from claude_code_adk_validator.streaming_processors import (
    ValidationProcessor,
    SecurityValidationProcessor,
    TDDValidationProcessor,
    FileCategorizationProcessor,
    ValidationPipelineBuilder,
    extract_json_from_part,
)


class SimpleTestProcessor(processor.PartProcessor):
    """Simple test processor that echoes input with a prefix"""
    
    def __init__(self, prefix: str = "TEST"):
        super().__init__()
        self.prefix = prefix
        
    def match(self, part: ProcessorPart) -> bool:
        """Match JSON parts with test field"""
        json_data = extract_json_from_part(part)
        return "test" in json_data
        
    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process the test part"""
        json_data = extract_json_from_part(part)
        if json_data and "test" in json_data:
            test_data = json_data.copy()
            test_data["processed"] = f"{self.prefix}: {test_data.get('test', '')}"
            yield ProcessorPart(json.dumps(test_data))
        else:
            yield part


class TestStreamingProcessors:
    """Test basic streaming processor functionality"""
    
    def test_processor_instantiation(self):
        """Test that processors can be instantiated"""
        assert ValidationProcessor()
        assert SecurityValidationProcessor()
        assert TDDValidationProcessor()
        assert FileCategorizationProcessor()
        
    def test_pipeline_builder(self):
        """Test pipeline builder creates processors"""
        builder = ValidationPipelineBuilder()
        
        assert builder.create_security_pipeline()
        assert builder.create_tdd_pipeline()
        assert builder.create_file_categorization_pipeline()
        assert builder.create_parallel_pipeline()
        
    @pytest.mark.asyncio
    async def test_simple_processor_flow(self):
        """Test simple processor with async streaming"""
        processor = SimpleTestProcessor("PROCESSED")
        
        input_data = {"test": "hello world"}
        input_part = ProcessorPart(json.dumps(input_data))
        
        results = []
        async for output_part in processor.call(input_part):
            json_data = extract_json_from_part(output_part)
            if json_data:
                results.append(json_data)
                
        assert len(results) == 1
        assert results[0]["test"] == "hello world"
        assert results[0]["processed"] == "PROCESSED: hello world"
        
    @pytest.mark.asyncio
    async def test_processor_chaining(self):
        """Test chaining multiple processors"""
        proc1 = SimpleTestProcessor("FIRST")
        proc2 = SimpleTestProcessor("SECOND")
        
        # Chain processors
        pipeline = proc1 + proc2
        
        input_data = {"test": "data"}
        input_stream = streams.stream_content([ProcessorPart(json.dumps(input_data))])
        
        results = []
        async for part in pipeline(input_stream):
            json_data = extract_json_from_part(part)
            if json_data:
                results.append(json_data)
                
        # Should have both results
        assert any(r.get("processed", "").startswith("FIRST:") for r in results)
        assert any(r.get("processed", "").startswith("SECOND:") for r in results)
        
    @pytest.mark.asyncio
    async def test_validation_processor_base(self):
        """Test base validation processor functionality"""
        processor = ValidationProcessor()
        
        # Should have default match method
        text_part = ProcessorPart("test")
        assert processor.match(text_part)
        
        # Should yield the same part by default
        result_parts = []
        async for part in processor.call(text_part):
            result_parts.append(part)
            
        assert len(result_parts) == 1
        assert result_parts[0] == text_part
        
    @pytest.mark.asyncio
    async def test_security_processor_without_api_key(self):
        """Test security processor without API key returns fail-safe response"""
        processor = SecurityValidationProcessor()
        
        request = {"prompt": "Test security validation"}
        request_part = ProcessorPart(json.dumps(request))
        
        results = []
        async for part in processor.call(request_part):
            json_data = extract_json_from_part(part)
            if json_data:
                results.append(json_data)
                
        assert len(results) == 1
        assert results[0]["error"] == "No API key configured"
        assert results[0]["approved"] is True  # Fail-safe
        
    @pytest.mark.asyncio 
    async def test_parallel_validation_pattern(self):
        """Test parallel validation pattern with mock processors"""
        
        async def mock_security_process():
            await asyncio.sleep(0.01)  # Simulate processing
            return {"approved": True, "reason": "Security check passed"}
            
        async def mock_tdd_process():
            await asyncio.sleep(0.01)  # Simulate processing
            return {"approved": True, "reason": "TDD check passed", "tdd_phase": "green"}
            
        # Run in parallel
        results = await asyncio.gather(
            mock_security_process(),
            mock_tdd_process()
        )
        
        assert len(results) == 2
        assert results[0]["approved"] is True
        assert results[1]["approved"] is True
        assert results[1]["tdd_phase"] == "green"
        

def run_tests():
    """Run the streaming processor tests"""
    pytest.main([__file__, "-v"])
    

if __name__ == "__main__":
    run_tests()
