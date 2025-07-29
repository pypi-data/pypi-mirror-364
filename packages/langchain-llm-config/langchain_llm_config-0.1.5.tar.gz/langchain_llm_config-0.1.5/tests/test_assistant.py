"""
Tests for assistant classes and chat streaming functionality
"""

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from langchain_llm_config.assistant.base import Assistant
from langchain_llm_config.assistant.chat_streaming import ChatStreaming


class MockResponse(BaseModel):
    """Mock response model for testing"""

    result: str = Field(..., description="Test result")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class MockTestAssistant(Assistant):
    """Mock test assistant class for testing base functionality"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(model_name="test-model", response_model=MockResponse, **kwargs)


class TestAssistantBase:
    """Test assistant base class functionality"""

    def test_assistant_initialization(self) -> None:
        """Test assistant initialization with various parameters"""
        assistant = MockTestAssistant(
            temperature=0.5,
            max_tokens=1000,
            base_url="https://test.com",
            api_key="test-key",
            system_prompt="You are a test assistant",
            top_p=0.9,
            connect_timeout=10,
            read_timeout=20,
            model_kwargs={"test_param": "test_value"},
        )

        assert assistant.system_prompt == "You are a test assistant"
        assert assistant.response_model == MockResponse
        assert assistant.llm is not None
        assert assistant.parser is not None
        assert assistant.prompt is not None
        assert assistant.chain is not None

    def test_assistant_initialization_defaults(self) -> None:
        """Test assistant initialization with default parameters"""
        assistant = MockTestAssistant()

        assert assistant.system_prompt is None
        assert assistant.response_model == MockResponse
        assert assistant.llm is not None

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_assistant_initialization_with_env_key(
        self, mock_chat_openai: MagicMock
    ) -> None:
        """Test assistant initialization using environment variable for API key"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-test-key"}):
            _ = MockTestAssistant(api_key=None)

        # Verify ChatOpenAI was called with env key
        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        # Check that SecretStr was used with the correct value
        secret_str = call_args[1]["api_key"]
        assert hasattr(secret_str, "get_secret_value")
        assert secret_str.get_secret_value() == "env-test-key"

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_assistant_initialization_with_dummy_key(
        self, mock_chat_openai: MagicMock
    ) -> None:
        """Test assistant initialization with dummy key when no env var"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        with patch.dict("os.environ", {}, clear=True):
            _ = MockTestAssistant(api_key=None)

        # Verify ChatOpenAI was called with dummy key
        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        # Check that SecretStr was used with the correct value
        secret_str = call_args[1]["api_key"]
        assert hasattr(secret_str, "get_secret_value")
        assert secret_str.get_secret_value() == "dummy-key"

    def test_setup_prompt_and_chain(self) -> None:
        """Test prompt and chain setup"""
        assistant = MockTestAssistant()

        # Verify prompt template is set up correctly
        assert assistant.prompt is not None
        assert "format_instructions" in assistant.prompt.partial_variables
        assert "question" in assistant.prompt.input_variables
        assert "system_prompt" in assistant.prompt.input_variables
        assert "context" in assistant.prompt.input_variables

        # Verify chain is set up
        assert assistant.chain is not None

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    def test_ask_method_success(self, mock_passthrough: MagicMock) -> None:
        """Test successful ask method execution"""
        # Mock the chain
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)

        # Mock response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "result": "test response",
            "confidence": 0.9,
        }
        mock_chain.invoke.return_value = mock_response

        assistant = MockTestAssistant()
        assistant.chain = mock_chain

        # Test ask method
        result = assistant.ask("test question")

        assert result == {"result": "test response", "confidence": 0.9}
        mock_chain.invoke.assert_called_once()

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    def test_ask_method_with_extra_system_prompt(
        self, mock_passthrough: MagicMock
    ) -> None:
        """Test ask method with extra system prompt"""
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"result": "test", "confidence": 0.8}
        mock_chain.invoke.return_value = mock_response

        assistant = MockTestAssistant(system_prompt="Base prompt")
        assistant.chain = mock_chain

        _ = assistant.ask("test question", extra_system_prompt="Extra prompt")

        # Verify the chain was called with combined system prompt
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["system_prompt"] == "Base prompt\nExtra prompt"

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    def test_ask_method_with_context(self, mock_passthrough: MagicMock) -> None:
        """Test ask method with context"""
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"result": "test", "confidence": 0.8}
        mock_chain.invoke.return_value = mock_response

        assistant = MockTestAssistant()
        assistant.chain = mock_chain

        _ = assistant.ask("test question", context="test context")

        # Verify the chain was called with context
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["context"] == "背景信息：test context"

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    def test_ask_method_exception_handling(self, mock_passthrough: MagicMock) -> None:
        """Test ask method exception handling"""
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.invoke.side_effect = Exception("Test error")

        assistant = MockTestAssistant()
        assistant.chain = mock_chain

        with pytest.raises(ValueError, match="处理查询时出错: Test error"):
            assistant.ask("test question")

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    @pytest.mark.asyncio
    async def test_ask_async_method_success(self, mock_passthrough: MagicMock) -> None:
        """Test successful ask_async method execution"""
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "result": "async test",
            "confidence": 0.95,
        }
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        assistant = MockTestAssistant()
        assistant.chain = mock_chain

        result = await assistant.ask_async("test question")

        assert result == {"result": "async test", "confidence": 0.95}
        mock_chain.ainvoke.assert_called_once()

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    @pytest.mark.asyncio
    async def test_ask_async_method_with_extra_system_prompt(
        self, mock_passthrough: MagicMock
    ) -> None:
        """Test ask_async method with extra system prompt"""
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"result": "test", "confidence": 0.8}
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        assistant = MockTestAssistant(system_prompt="Base prompt")
        assistant.chain = mock_chain

        _ = await assistant.ask_async(
            "test question", extra_system_prompt="Extra prompt"
        )

        # Verify the chain was called with combined system prompt
        call_args = mock_chain.ainvoke.call_args[0][0]
        assert call_args["system_prompt"] == "Base prompt\nExtra prompt"

    @patch("langchain_llm_config.assistant.base.RunnablePassthrough")
    @pytest.mark.asyncio
    async def test_ask_async_method_exception_handling(
        self, mock_passthrough: MagicMock
    ) -> None:
        """Test ask_async method exception handling"""
        mock_chain = MagicMock()
        mock_passthrough.return_value.__or__ = MagicMock(return_value=mock_chain)
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("Async test error"))

        assistant = MockTestAssistant()
        assistant.chain = mock_chain

        with pytest.raises(ValueError, match="处理查询时出错: Async test error"):
            await assistant.ask_async("test question")


class TestChatStreaming:
    """Test chat streaming functionality"""

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_chat_streaming_initialization(self, mock_chat_openai: MagicMock) -> None:
        """Test chat streaming initialization"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        streaming = ChatStreaming(
            model_name="test-model",
            temperature=0.5,
            max_tokens=1000,
            base_url="https://test.com",
            api_key="test-key",
            system_prompt="Test system prompt",
            top_p=0.9,
            connect_timeout=10,
            read_timeout=20,
            model_kwargs={"test_param": "test_value"},
        )

        assert streaming.model_name == "test-model"
        assert streaming.system_prompt == "Test system prompt"
        assert streaming.llm is not None
        assert streaming.prompt is not None

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_chat_streaming_initialization_defaults(
        self, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat streaming initialization with defaults"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        streaming = ChatStreaming(model_name="test-model")

        assert streaming.model_name == "test-model"
        assert streaming.system_prompt is None
        assert streaming.llm is not None

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_setup_prompt(self, mock_chat_openai: MagicMock) -> None:
        """Test prompt setup for chat streaming"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        streaming = ChatStreaming(model_name="test-model")

        assert streaming.prompt is not None
        assert "question" in streaming.prompt.input_variables
        assert "system_prompt" in streaming.prompt.input_variables
        assert "context" in streaming.prompt.input_variables

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_method_success(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test successful chat method execution"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        # Mock time
        mock_time.side_effect = [100.0, 101.5]  # start_time, end_time

        # Mock response
        mock_response = MagicMock()
        mock_response.content = "Test response content"

        streaming = ChatStreaming(model_name="test-model")

        # Mock the base_chain.ainvoke method
        streaming.base_chain = MagicMock()
        streaming.base_chain.ainvoke = AsyncMock(return_value=mock_response)

        result = asyncio.run(streaming.chat("test question"))

        assert result["content"] == "Test response content"
        assert result["processing_time"] == 1.5
        assert result["model_used"] == "test-model"

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_method_with_extra_system_prompt(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat method with extra system prompt"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        mock_time.side_effect = [100.0, 101.0]

        mock_response = MagicMock()
        mock_response.content = "Test response"

        streaming = ChatStreaming(model_name="test-model", system_prompt="Base prompt")

        # Mock the base_chain.ainvoke method
        streaming.base_chain = MagicMock()
        streaming.base_chain.ainvoke = AsyncMock(return_value=mock_response)

        _ = asyncio.run(
            streaming.chat("test question", extra_system_prompt="Extra prompt")
        )

        # Verify the base_chain was called with combined system prompt
        call_args = streaming.base_chain.ainvoke.call_args[0][0]
        assert call_args["system_prompt"] == "Base prompt\nExtra prompt"

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_method_with_context(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat method with context"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        mock_time.side_effect = [100.0, 101.0]

        mock_response = MagicMock()
        mock_response.content = "Test response"

        streaming = ChatStreaming(model_name="test-model")

        # Mock the base_chain.ainvoke method
        streaming.base_chain = MagicMock()
        streaming.base_chain.ainvoke = AsyncMock(return_value=mock_response)

        _ = asyncio.run(streaming.chat("test question", context="test context"))

        # Verify the base_chain was called with context
        call_args = streaming.base_chain.ainvoke.call_args[0][0]
        assert call_args["context"] == "背景信息：test context"

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_method_exception_handling(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat method exception handling"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        mock_time.side_effect = [100.0, 101.0]

        streaming = ChatStreaming(model_name="test-model")

        # Mock the base_chain.ainvoke method to raise an exception
        streaming.base_chain = MagicMock()
        streaming.base_chain.ainvoke = AsyncMock(
            side_effect=Exception("Chat test error")
        )

        with pytest.raises(ValueError, match="处理查询时出错: Chat test error"):
            asyncio.run(streaming.chat("test question"))

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_stream_method_success(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test successful chat_stream method execution"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        # Mock time
        mock_time.side_effect = [
            100.0,
            101.0,
            102.0,
            103.0,
        ]  # start_time, chunk1, chunk2, final

        # Mock streaming chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.content = "Hello"
        mock_chunk2 = MagicMock()
        mock_chunk2.content = " World"

        # Create a proper async generator that accepts arguments
        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            yield mock_chunk1
            yield mock_chunk2

        streaming = ChatStreaming(model_name="test-model")

        # Mock the base_chain.astream method
        streaming.base_chain = MagicMock()
        streaming.base_chain.astream = mock_stream

        # Collect streaming results
        results: List[Dict[str, Any]] = []

        async def collect_stream() -> None:
            async for chunk in streaming.chat_stream("test question"):
                results.append(chunk)

        asyncio.run(collect_stream())

        # Verify streaming results - should have stream chunks + final result
        assert len(results) >= 2

        # Check stream chunks
        assert results[0]["type"] == "stream"
        assert results[0]["content"] == "Hello"
        assert results[1]["type"] == "stream"
        assert results[1]["content"] == " World"

        # Check final result
        final_result = results[-1]
        assert final_result["type"] == "final"
        assert final_result["content"] == "Hello World"
        assert final_result["is_complete"]

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_stream_method_with_extra_system_prompt(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat_stream method with extra system prompt"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        mock_time.side_effect = [100.0, 101.0, 102.0]

        mock_chunk = MagicMock()
        mock_chunk.content = "Test response"

        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            yield mock_chunk

        mock_llm.astream = mock_stream

        streaming = ChatStreaming(model_name="test-model", system_prompt="Base prompt")

        results: List[Dict[str, Any]] = []

        async def collect_stream() -> None:
            async for chunk in streaming.chat_stream(
                "test question", extra_system_prompt="Extra prompt"
            ):
                results.append(chunk)

        asyncio.run(collect_stream())

        # Verify we got stream chunk + final result
        assert len(results) >= 2
        assert results[0]["type"] == "stream"
        assert results[-1]["type"] == "final"

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_stream_method_exception_handling(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat_stream method exception handling"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        # Provide enough time values for all calls
        mock_time.side_effect = [100.0, 101.0, 102.0, 103.0]

        # Create an async generator function that raises an exception
        async def mock_generator(*args: Any, **kwargs: Any) -> Any:
            raise Exception("Stream test error")
            yield None  # type: ignore[unreachable]

        streaming = ChatStreaming(model_name="test-model")

        # Mock the base_chain.astream method to raise an exception
        streaming.base_chain = MagicMock()
        streaming.base_chain.astream = mock_generator

        results: List[Dict[str, Any]] = []

        async def collect_stream() -> None:
            async for chunk in streaming.chat_stream("test question"):
                results.append(chunk)

        asyncio.run(collect_stream())

        # Verify we get only the error result
        assert len(results) == 1
        assert results[0]["type"] == "error"
        assert "Stream test error" in results[0]["error"]
        assert results[0]["is_complete"]

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    @patch("time.time")
    def test_chat_stream_method_empty_response(
        self, mock_time: MagicMock, mock_chat_openai: MagicMock
    ) -> None:
        """Test chat_stream method with empty response"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        mock_time.side_effect = [100.0, 101.0, 102.0]

        # Mock empty response
        async def mock_stream(*args: Any, **kwargs: Any) -> Any:
            # Empty generator - use yield to make it a proper async generator
            if False:  # This will never be True, so no chunks will be yielded
                yield None  # type: ignore[unreachable]

        streaming = ChatStreaming(model_name="test-model")

        # Mock the base_chain.astream method
        streaming.base_chain = MagicMock()
        streaming.base_chain.astream = mock_stream

        results: List[Dict[str, Any]] = []

        async def collect_stream() -> None:
            async for chunk in streaming.chat_stream("test question"):
                results.append(chunk)

        asyncio.run(collect_stream())

        # Verify only final result (empty stream should still produce final result)
        assert len(results) == 1
        assert results[0]["type"] == "final"
        assert results[0]["content"] == ""
        assert results[0]["is_complete"]
