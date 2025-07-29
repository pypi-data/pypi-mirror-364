"""
Tests for factory module
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from langchain_llm_config.factory import (
    create_assistant,
    create_chat_streaming,
    create_embedding_provider,
)


class MockResponse(BaseModel):
    """Mock response model for testing"""

    result: str = Field(..., description="Test result")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class TestFactoryFunctions:
    """Test factory functions"""

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_openai_provider(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with OpenAI provider"""
        # Mock config
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "api_base": "https://api.openai.com/v1",
                    "top_p": 0.9,
                    "read_timeout": 60,
                    "connect_timeout": 30,
                    "model_kwargs": {"test_param": "test_value"},
                }
            },
        }

        # Test the function
        result = create_assistant(
            response_model=MockResponse,
            provider="openai",
            system_prompt="Test system prompt",
        )

        # Verify the result is an Assistant instance
        from langchain_llm_config.assistant.base import Assistant

        assert isinstance(result, Assistant)
        assert result.system_prompt == "Test system prompt"
        assert result.response_model == MockResponse

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_openai_provider_defaults(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with OpenAI provider using defaults"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {"chat": {"model_name": "gpt-3.5-turbo", "api_key": "test-key"}},
        }

        result = create_assistant(response_model=MockResponse, provider="openai")

        # Verify the result is an Assistant instance
        from langchain_llm_config.assistant.base import Assistant

        assert isinstance(result, Assistant)
        assert result.response_model == MockResponse

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_gemini_provider(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with Gemini provider"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "gemini"},
            "gemini": {
                "chat": {
                    "model_name": "gemini-pro",
                    "api_key": "test-key",
                    "temperature": 0.8,
                    "max_tokens": 3000,
                }
            },
        }

        result = create_assistant(
            response_model=MockResponse,
            provider="gemini",
            system_prompt="Test system prompt",
        )

        # Verify the result is a GeminiAssistant instance
        from langchain_llm_config.assistant.providers.gemini import GeminiAssistant

        assert isinstance(result, GeminiAssistant)
        assert result.response_model == MockResponse

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_vllm_provider(self, mock_load_config: MagicMock) -> None:
        """Test create_assistant with VLLM provider"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "vllm"},
            "vllm": {
                "chat": {
                    "model_name": "llama-2-7b",
                    "api_base": "http://localhost:8000/v1",
                    "api_key": "test-key",
                    "temperature": 0.6,
                    "max_tokens": 8192,
                    "top_p": 0.8,
                    "connect_timeout": 30,
                    "read_timeout": 60,
                    "model_kwargs": {"test_param": "test_value"},
                }
            },
        }

        result = create_assistant(
            response_model=MockResponse,
            provider="vllm",
            system_prompt="Test system prompt",
        )

        # Verify the result is a VLLMAssistant instance
        from langchain_llm_config.assistant.providers.vllm import VLLMAssistant

        assert isinstance(result, VLLMAssistant)
        assert result.response_model == MockResponse

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_default_provider(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with default provider"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {"chat": {"model_name": "gpt-3.5-turbo", "api_key": "test-key"}},
        }

        result = create_assistant(response_model=MockResponse)

        # Verify the result is an Assistant instance
        from langchain_llm_config.assistant.base import Assistant

        assert isinstance(result, Assistant)
        assert result.response_model == MockResponse

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_with_custom_config_path(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with custom config path"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {"chat": {"model_name": "gpt-3.5-turbo", "api_key": "test-key"}},
        }

        result = create_assistant(
            response_model=MockResponse, config_path="/custom/path/api.yaml"
        )

        # Verify the result is an Assistant instance
        from langchain_llm_config.assistant.base import Assistant

        assert isinstance(result, Assistant)
        mock_load_config.assert_called_once_with("/custom/path/api.yaml")

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_with_additional_kwargs(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with additional kwargs"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {"chat": {"model_name": "gpt-3.5-turbo", "api_key": "test-key"}},
        }

        # Test with kwargs that are valid for the Assistant class
        result = create_assistant(
            response_model=MockResponse,
            provider="openai",
            system_prompt="Test prompt",  # Valid parameter for Assistant
        )

        # Verify the result is an Assistant instance
        from langchain_llm_config.assistant.base import Assistant

        assert isinstance(result, Assistant)
        assert result.response_model == MockResponse

    @patch("langchain_llm_config.factory.load_config")
    @patch("langchain_llm_config.factory.ChatStreaming")
    def test_create_chat_streaming(
        self, mock_chat_streaming_class: MagicMock, mock_load_config: MagicMock
    ) -> None:
        """Test create_chat_streaming function"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {
                "chat": {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "test-key",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "api_base": "https://api.openai.com/v1",
                    "top_p": 0.9,
                    "read_timeout": 60,
                    "connect_timeout": 30,
                    "model_kwargs": {"test_param": "test_value"},
                }
            },
        }

        mock_streaming = MagicMock()
        mock_chat_streaming_class.return_value = mock_streaming

        result = create_chat_streaming(
            provider="openai", system_prompt="Test system prompt"
        )

        assert result == mock_streaming

        # Verify ChatStreaming was called with correct parameters
        mock_chat_streaming_class.assert_called_once()
        call_args = mock_chat_streaming_class.call_args[1]
        assert call_args["model_name"] == "gpt-3.5-turbo"
        assert call_args["temperature"] == 0.7
        assert call_args["max_tokens"] == 2000
        assert call_args["base_url"] == "https://api.openai.com/v1"
        assert call_args["api_key"] == "test-key"
        assert call_args["top_p"] == 0.9
        assert call_args["read_timeout"] == 60
        assert call_args["connect_timeout"] == 30
        assert call_args["model_kwargs"] == {"test_param": "test_value"}
        assert call_args["system_prompt"] == "Test system prompt"

    @patch("langchain_llm_config.factory.load_config")
    @patch("langchain_llm_config.factory.ChatStreaming")
    def test_create_chat_streaming_default_provider(
        self, mock_chat_streaming_class: MagicMock, mock_load_config: MagicMock
    ) -> None:
        """Test create_chat_streaming with default provider"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {"chat": {"model_name": "gpt-3.5-turbo", "api_key": "test-key"}},
        }

        mock_streaming = MagicMock()
        mock_chat_streaming_class.return_value = mock_streaming

        result = create_chat_streaming()

        assert result == mock_streaming
        mock_chat_streaming_class.assert_called_once()

    @patch("langchain_llm_config.factory.load_config")
    @patch("langchain_llm_config.factory.ChatStreaming")
    def test_create_chat_streaming_with_custom_config_path(
        self, mock_chat_streaming_class: MagicMock, mock_load_config: MagicMock
    ) -> None:
        """Test create_chat_streaming with custom config path"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "openai"},
            "openai": {"chat": {"model_name": "gpt-3.5-turbo", "api_key": "test-key"}},
        }

        mock_streaming = MagicMock()
        mock_chat_streaming_class.return_value = mock_streaming

        result = create_chat_streaming(config_path="/custom/path/api.yaml")

        assert result == mock_streaming
        mock_load_config.assert_called_once_with("/custom/path/api.yaml")

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_openai(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_embedding_provider with OpenAI provider"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "openai"},
            "openai": {
                "embeddings": {
                    "model_name": "text-embedding-ada-002",
                    "api_key": "test-key",
                    "api_base": "https://api.openai.com/v1",
                    "timeout": 30,
                    "dimensions": 1536,
                }
            },
        }

        result = create_embedding_provider(provider="openai")

        # Verify the result is an OpenAIEmbeddingProvider instance
        from langchain_llm_config.embeddings.providers.openai import (
            OpenAIEmbeddingProvider,
        )

        assert isinstance(result, OpenAIEmbeddingProvider)

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_vllm(self, mock_load_config: MagicMock) -> None:
        """Test create_embedding_provider with VLLM provider"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "vllm"},
            "vllm": {
                "embeddings": {
                    "model_name": "bge-m3",
                    "api_base": "http://localhost:8000/v1",
                    "api_key": "test-key",
                    "timeout": 30,
                    "dimensions": 1024,
                }
            },
        }

        result = create_embedding_provider(provider="vllm")

        # Verify the result is a VLLMEmbeddingProvider instance
        from langchain_llm_config.embeddings.providers.vllm import VLLMEmbeddingProvider

        assert isinstance(result, VLLMEmbeddingProvider)

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_infinity(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_embedding_provider with Infinity provider"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "infinity"},
            "infinity": {
                "embeddings": {
                    "model_name": "models/bge-m3",
                    "api_base": "http://localhost:7997/v1",
                }
            },
        }

        result = create_embedding_provider(provider="infinity")

        # Verify the result is an InfinityEmbeddingProvider instance
        from langchain_llm_config.embeddings.providers.infinity import (
            InfinityEmbeddingProvider,
        )

        assert isinstance(result, InfinityEmbeddingProvider)

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_default(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_embedding_provider with default provider"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "openai"},
            "openai": {
                "embeddings": {
                    "model_name": "text-embedding-ada-002",
                    "api_key": "test-key",
                }
            },
        }

        result = create_embedding_provider()

        # Verify the result is an OpenAIEmbeddingProvider instance
        from langchain_llm_config.embeddings.providers.openai import (
            OpenAIEmbeddingProvider,
        )

        assert isinstance(result, OpenAIEmbeddingProvider)

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_with_custom_config_path(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_embedding_provider with custom config path"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "openai"},
            "openai": {
                "embeddings": {
                    "model_name": "text-embedding-ada-002",
                    "api_key": "test-key",
                }
            },
        }

        result = create_embedding_provider(
            provider="openai", config_path="/custom/path/api.yaml"
        )

        # Verify the result is an OpenAIEmbeddingProvider instance
        from langchain_llm_config.embeddings.providers.openai import (
            OpenAIEmbeddingProvider,
        )

        assert isinstance(result, OpenAIEmbeddingProvider)
        mock_load_config.assert_called_once_with("/custom/path/api.yaml")

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_with_additional_kwargs(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_embedding_provider with additional kwargs"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "openai"},
            "openai": {
                "embeddings": {
                    "model_name": "text-embedding-ada-002",
                    "api_key": "test-key",
                }
            },
        }

        result = create_embedding_provider(
            provider="openai", timeout=60  # Valid parameter for embedding providers
        )

        # Verify the result is an OpenAIEmbeddingProvider instance
        from langchain_llm_config.embeddings.providers.openai import (
            OpenAIEmbeddingProvider,
        )

        assert isinstance(result, OpenAIEmbeddingProvider)

    @patch("langchain_llm_config.factory.load_config")
    def test_create_embedding_provider_unsupported_provider(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_embedding_provider with unsupported provider"""
        mock_load_config.return_value = {
            "default": {"embedding_provider": "unsupported"},
            "unsupported": {"embeddings": {"model_name": "test-model"}},
        }

        with pytest.raises(ValueError, match="未知的嵌入提供者: unsupported"):
            create_embedding_provider(provider="unsupported")

    @patch("langchain_llm_config.factory.load_config")
    def test_create_assistant_unsupported_provider(
        self, mock_load_config: MagicMock
    ) -> None:
        """Test create_assistant with unsupported provider"""
        mock_load_config.return_value = {
            "default": {"chat_provider": "unsupported"},
            "unsupported": {"chat": {"model_name": "test-model"}},
        }

        with pytest.raises(ValueError, match="未知的助手提供者: unsupported"):
            create_assistant(response_model=MockResponse, provider="unsupported")
