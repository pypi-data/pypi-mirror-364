"""
Tests for auto_apply_parser functionality across all providers
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from langchain_llm_config import create_assistant
from langchain_llm_config.assistant.base import Assistant
from langchain_llm_config.assistant.providers.gemini import GeminiAssistant
from langchain_llm_config.assistant.providers.vllm import VLLMAssistant


class MockResponse(BaseModel):
    """Mock response model for testing"""

    message: str = Field(..., description="Response message")
    confidence: float = Field(default=0.8, description="Confidence score")


class TestAutoApplyParser:
    """Test auto_apply_parser functionality for all providers"""

    @patch("langchain_llm_config.factory.load_config")
    def test_openai_auto_apply_parser_true(self, mock_load_config: MagicMock) -> None:
        """Test OpenAI provider with auto_apply_parser=True"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                }
            },
        }

        assistant = create_assistant(
            response_model=MockResponse,
            provider="openai",
            auto_apply_parser=True,
        )

        assert isinstance(assistant, Assistant)
        # Check that parser is applied (chain includes parser)
        assert hasattr(assistant, "chain")
        assert hasattr(assistant, "base_chain")
        assert hasattr(assistant, "parser")
        # When parser is applied, chain should be different from base_chain
        assert assistant.chain != assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_openai_auto_apply_parser_false(self, mock_load_config: MagicMock) -> None:
        """Test OpenAI provider with auto_apply_parser=False"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                }
            },
        }

        assistant = create_assistant(
            response_model=MockResponse,
            provider="openai",
            auto_apply_parser=False,
        )

        assert isinstance(assistant, Assistant)
        # Check that parser is not applied (chain equals base_chain)
        assert hasattr(assistant, "chain")
        assert hasattr(assistant, "base_chain")
        assert hasattr(assistant, "parser")
        # When parser is not applied, chain should be same as base_chain
        assert assistant.chain == assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_vllm_auto_apply_parser_true(self, mock_load_config: MagicMock) -> None:
        """Test vLLM provider with auto_apply_parser=True"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "vllm"},
            "vllm": {
                "chat": {
                    "model_name": "llama-2-7b",
                    "api_base": "http://localhost:8000/v1",
                }
            },
        }

        assistant = create_assistant(
            response_model=MockResponse,
            provider="vllm",
            auto_apply_parser=True,
        )

        assert isinstance(assistant, VLLMAssistant)
        # Check that parser is applied
        assert hasattr(assistant, "chain")
        assert hasattr(assistant, "base_chain")
        assert hasattr(assistant, "parser")
        assert assistant.chain != assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_vllm_auto_apply_parser_false(self, mock_load_config: MagicMock) -> None:
        """Test vLLM provider with auto_apply_parser=False"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "vllm"},
            "vllm": {
                "chat": {
                    "model_name": "llama-2-7b",
                    "api_base": "http://localhost:8000/v1",
                }
            },
        }

        assistant = create_assistant(
            response_model=MockResponse,
            provider="vllm",
            auto_apply_parser=False,
        )

        assert isinstance(assistant, VLLMAssistant)
        # Check that parser is not applied
        assert hasattr(assistant, "chain")
        assert hasattr(assistant, "base_chain")
        assert hasattr(assistant, "parser")
        assert assistant.chain == assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_gemini_auto_apply_parser_true(self, mock_load_config: MagicMock) -> None:
        """Test Gemini provider with auto_apply_parser=True"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "gemini"},
            "gemini": {
                "chat": {
                    "model_name": "gemini-pro",
                    "api_key": "test-key",
                }
            },
        }

        assistant = create_assistant(
            response_model=MockResponse,
            provider="gemini",
            auto_apply_parser=True,
        )

        assert isinstance(assistant, GeminiAssistant)
        # Check that parser is applied
        assert hasattr(assistant, "chain")
        assert hasattr(assistant, "base_chain")
        assert hasattr(assistant, "parser")
        assert assistant.chain != assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_gemini_auto_apply_parser_false(self, mock_load_config: MagicMock) -> None:
        """Test Gemini provider with auto_apply_parser=False"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "gemini"},
            "gemini": {
                "chat": {
                    "model_name": "gemini-pro",
                    "api_key": "test-key",
                }
            },
        }

        assistant = create_assistant(
            response_model=MockResponse,
            provider="gemini",
            auto_apply_parser=False,
        )

        assert isinstance(assistant, GeminiAssistant)
        # Check that parser is not applied
        assert hasattr(assistant, "chain")
        assert hasattr(assistant, "base_chain")
        assert hasattr(assistant, "parser")
        assert assistant.chain == assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_default_auto_apply_parser_behavior(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test that auto_apply_parser defaults to True for backward compatibility"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                }
            },
        }

        # When auto_apply_parser is not specified, it should default to True
        assistant = create_assistant(
            response_model=MockResponse,
            provider="openai",
        )

        assert isinstance(assistant, Assistant)
        # Parser should be applied by default
        assert assistant.chain != assistant.base_chain

    def test_manual_parser_application(self) -> None:
        """Test manual application of parser after initialization"""
        # Create assistant without auto-applying parser
        assistant = Assistant(
            model_name="gpt-3.5-turbo",
            response_model=MockResponse,
            auto_apply_parser=False,
        )

        # Initially, parser should not be applied
        assert assistant.chain == assistant.base_chain

        # Manually apply parser
        assistant.apply_parser()

        # Now parser should be applied
        assert assistant.chain != assistant.base_chain

    def test_vllm_manual_parser_application(self) -> None:
        """Test manual application of parser for vLLM assistant"""
        config = {
            "model_name": "llama-2-7b",
            "api_base": "http://localhost:8000/v1",
        }

        assistant = VLLMAssistant(
            config=config,
            response_model=MockResponse,
            auto_apply_parser=False,
        )

        # Initially, parser should not be applied
        assert assistant.chain == assistant.base_chain

        # Manually apply parser
        assistant.apply_parser()

        # Now parser should be applied
        assert assistant.chain != assistant.base_chain

    def test_gemini_manual_parser_application(self) -> None:
        """Test manual application of parser for Gemini assistant"""
        config = {
            "model_name": "gemini-pro",
            "api_key": "test-key",
        }

        assistant = GeminiAssistant(
            config=config,
            response_model=MockResponse,
            auto_apply_parser=False,
        )

        # Initially, parser should not be applied
        assert assistant.chain == assistant.base_chain

        # Manually apply parser
        assistant.apply_parser()

        # Now parser should be applied
        assert assistant.chain != assistant.base_chain

    def test_dynamic_parser_application_with_model(self) -> None:
        """Test applying parser with a new response model after creation"""
        # Create assistant without response model
        assistant = Assistant(
            model_name="gpt-3.5-turbo",
            response_model=None,
            auto_apply_parser=False,
        )

        # Initially, no parser should exist
        assert assistant.parser is None
        assert assistant.response_model is None
        assert assistant.chain == assistant.base_chain

        # Apply parser with a response model
        assistant.apply_parser(response_model=MockResponse)

        # Now parser should be applied
        assert assistant.parser is not None
        assert assistant.response_model == MockResponse  # type: ignore[unreachable]
        assert assistant.chain != assistant.base_chain

    def test_dynamic_parser_application_vllm(self) -> None:
        """Test applying parser with a new response model for vLLM assistant"""
        config = {
            "model_name": "llama-2-7b",
            "api_base": "http://localhost:8000/v1",
        }

        assistant = VLLMAssistant(
            config=config,
            response_model=None,
            auto_apply_parser=False,
        )

        # Initially, no parser should exist
        assert assistant.parser is None
        assert assistant.response_model is None
        assert assistant.chain == assistant.base_chain

        # Apply parser with a response model
        assistant.apply_parser(response_model=MockResponse)

        # Now parser should be applied
        assert assistant.parser is not None
        assert assistant.response_model == MockResponse  # type: ignore[unreachable]
        assert assistant.chain != assistant.base_chain

    def test_dynamic_parser_application_gemini(self) -> None:
        """Test applying parser with a new response model for Gemini assistant"""
        config = {
            "model_name": "gemini-pro",
            "api_key": "test-key",
        }

        assistant = GeminiAssistant(
            config=config,
            response_model=None,
            auto_apply_parser=False,
        )

        # Initially, no parser should exist
        assert assistant.parser is None
        assert assistant.response_model is None
        assert assistant.chain == assistant.base_chain

        # Apply parser with a response model
        assistant.apply_parser(response_model=MockResponse)

        # Now parser should be applied
        assert assistant.parser is not None
        assert assistant.response_model == MockResponse  # type: ignore[unreachable]
        assert assistant.chain != assistant.base_chain

    @patch("langchain_llm_config.factory.load_config")
    def test_factory_without_response_model(self, mock_load_config: MagicMock) -> None:
        """Test creating assistant without response_model via factory"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                }
            },
        }

        # Create assistant without response_model
        assistant = create_assistant(
            response_model=None,
            provider="openai",
            auto_apply_parser=False,
        )

        assert isinstance(assistant, Assistant)
        assert assistant.response_model is None
        assert assistant.parser is None
        assert assistant.chain == assistant.base_chain

        # Later apply parser with response model
        assistant.apply_parser(response_model=MockResponse)

        # Check state after applying parser
        assert assistant.response_model == MockResponse
        assert assistant.parser is not None
        assert assistant.chain != assistant.base_chain  # type: ignore[unreachable]

    def test_error_when_no_model_provided(self) -> None:
        """Test error when trying to apply parser without any response model"""
        assistant = Assistant(
            model_name="gpt-3.5-turbo",
            response_model=None,
            auto_apply_parser=False,
        )

        # Should raise error when trying to apply parser without model
        with pytest.raises(
            ValueError, match="Cannot apply parser: no response_model was provided"
        ):
            assistant.apply_parser()

    @patch("langchain_llm_config.factory.load_config")
    def test_factory_error_when_auto_apply_without_model(
        self, mock_load_config: MagicMock
    ) -> None:
        """
        Test factory raises error when auto_apply_parser=True but no response_model
        """
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                }
            },
        }

        # Should raise error when auto_apply_parser=True but no response_model
        with pytest.raises(
            ValueError, match="response_model is required when auto_apply_parser=True"
        ):
            create_assistant(
                response_model=None,
                provider="openai",
                auto_apply_parser=True,
            )
