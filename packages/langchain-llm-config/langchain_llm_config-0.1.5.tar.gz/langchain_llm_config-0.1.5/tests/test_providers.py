"""
Tests for provider classes
"""

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from langchain_llm_config.assistant.providers.gemini import GeminiAssistant
from langchain_llm_config.assistant.providers.vllm import VLLMAssistant
from langchain_llm_config.embeddings.providers.infinity import InfinityEmbeddingProvider
from langchain_llm_config.embeddings.providers.openai import OpenAIEmbeddingProvider
from langchain_llm_config.embeddings.providers.vllm import VLLMEmbeddingProvider


class MockResponse(BaseModel):
    """Mock response model for testing"""

    result: str = Field(..., description="Test result")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class TestGeminiAssistant:
    """Test Gemini assistant provider"""

    @patch("langchain_llm_config.assistant.providers.gemini.ChatGoogleGenerativeAI")
    def test_gemini_assistant_initialization(self, mock_chat_gemini: MagicMock) -> None:
        """Test Gemini assistant initialization"""
        mock_llm = MagicMock()
        mock_chat_gemini.return_value = mock_llm

        config: Dict[str, Any] = {
            "model_name": "gemini-pro",
            "api_key": "test-key",
            "temperature": 0.7,
            "max_tokens": 3000,
            "top_p": 0.9,
            "top_k": 40,
            "connect_timeout": 30,
            "read_timeout": 60,
            "model_kwargs": {"test_param": "test_value"},
        }

        assistant = GeminiAssistant(
            config=config,
            response_model=MockResponse,
            system_prompt="Test system prompt",
        )

        # Test accessible attributes
        assert assistant.system_prompt == "Test system prompt"
        assert assistant.response_model == MockResponse
        assert assistant.llm is not None
        assert assistant.parser is not None
        assert assistant.prompt is not None
        assert assistant.chain is not None

    @patch("langchain_llm_config.assistant.providers.gemini.ChatGoogleGenerativeAI")
    def test_gemini_assistant_initialization_defaults(
        self, mock_chat_gemini: MagicMock
    ) -> None:
        """Test Gemini assistant initialization with defaults"""
        mock_llm = MagicMock()
        mock_chat_gemini.return_value = mock_llm

        config: Dict[str, str] = {"model_name": "gemini-pro"}

        assistant = GeminiAssistant(config=config, response_model=MockResponse)

        # Test accessible attributes
        assert assistant.system_prompt is None
        assert assistant.response_model == MockResponse
        assert assistant.llm is not None

    @patch("langchain_llm_config.assistant.providers.gemini.ChatGoogleGenerativeAI")
    def test_gemini_assistant_initialization_with_env_key(
        self, mock_chat_gemini: MagicMock
    ) -> None:
        """Test Gemini assistant initialization using environment variable"""
        mock_llm = MagicMock()
        mock_chat_gemini.return_value = mock_llm

        config: Dict[str, Any] = {"model_name": "gemini-pro", "api_key": None}

        with patch.dict("os.environ", {"GEMINI_API_KEY": "env-test-key"}):
            _ = GeminiAssistant(config=config, response_model=MockResponse)

        # Verify ChatGoogleGenerativeAI was called with env key
        mock_chat_gemini.assert_called_once()
        call_args = mock_chat_gemini.call_args
        # Check that SecretStr was used with the correct value
        secret_str = call_args[1]["api_key"]
        assert hasattr(secret_str, "get_secret_value")
        assert secret_str.get_secret_value() == "env-test-key"

    @patch("langchain_llm_config.assistant.providers.gemini.ChatGoogleGenerativeAI")
    def test_gemini_assistant_initialization_with_dummy_key(
        self, mock_chat_gemini: MagicMock
    ) -> None:
        """Test Gemini assistant initialization with dummy key when no env var"""
        mock_llm = MagicMock()
        mock_chat_gemini.return_value = mock_llm

        config: Dict[str, Any] = {"model_name": "gemini-pro", "api_key": None}

        with patch.dict("os.environ", {}, clear=True):
            _ = GeminiAssistant(config=config, response_model=MockResponse)

        # Verify ChatGoogleGenerativeAI was called with dummy key
        mock_chat_gemini.assert_called_once()
        call_args = mock_chat_gemini.call_args
        # Check that SecretStr was used with the correct value
        secret_str = call_args[1]["api_key"]
        assert hasattr(secret_str, "get_secret_value")
        assert secret_str.get_secret_value() == "dummy-key"

    @patch("langchain_llm_config.assistant.providers.gemini.ChatGoogleGenerativeAI")
    def test_gemini_assistant_ask_method(self, mock_chat_gemini: MagicMock) -> None:
        """Test Gemini assistant ask method"""
        mock_llm = MagicMock()
        mock_chat_gemini.return_value = mock_llm

        config: Dict[str, str] = {"model_name": "gemini-pro"}

        # Mock the chain
        mock_chain = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "result": "gemini response",
            "confidence": 0.95,
        }
        mock_chain.invoke.return_value = mock_response

        assistant = GeminiAssistant(config=config, response_model=MockResponse)
        assistant.chain = mock_chain

        result = assistant.ask("test question")

        assert result == {"result": "gemini response", "confidence": 0.95}
        mock_chain.invoke.assert_called_once()


class TestVLLMAssistant:
    """Test VLLM assistant provider"""

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_vllm_assistant_initialization(self, mock_chat_openai: MagicMock) -> None:
        """Test VLLM assistant initialization"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        config: Dict[str, Any] = {
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

        assistant = VLLMAssistant(
            config=config,
            response_model=MockResponse,
            system_prompt="Test system prompt",
        )

        # Test accessible attributes
        assert assistant.system_prompt == "Test system prompt"
        assert assistant.response_model == MockResponse
        assert assistant.llm is not None
        assert assistant.parser is not None
        assert assistant.prompt is not None
        assert assistant.chain is not None

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_vllm_assistant_initialization_defaults(
        self, mock_chat_openai: MagicMock
    ) -> None:
        """Test VLLM assistant initialization with defaults"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        config: Dict[str, str] = {
            "model_name": "llama-2-7b",
            "api_base": "http://localhost:8000/v1",
        }

        assistant = VLLMAssistant(config=config, response_model=MockResponse)

        # Test accessible attributes
        assert assistant.system_prompt is None
        assert assistant.response_model == MockResponse
        assert assistant.llm is not None

    @patch("langchain_llm_config.assistant.base.ChatOpenAI")
    def test_vllm_assistant_ask_method(self, mock_chat_openai: MagicMock) -> None:
        """Test VLLM assistant ask method"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        config: Dict[str, str] = {
            "model_name": "llama-2-7b",
            "api_base": "http://localhost:8000/v1",
        }

        # Mock the chain
        mock_chain = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "result": "vllm response",
            "confidence": 0.88,
        }
        mock_chain.invoke.return_value = mock_response

        assistant = VLLMAssistant(config=config, response_model=MockResponse)
        assistant.chain = mock_chain

        result = assistant.ask("test question")

        assert result == {"result": "vllm response", "confidence": 0.88}
        mock_chain.invoke.assert_called_once()


class TestOpenAIEmbeddingProvider:
    """Test OpenAI embedding provider"""

    @patch("langchain_llm_config.embeddings.providers.openai.OpenAIEmbeddings")
    def test_openai_embedding_provider_initialization(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test OpenAI embedding provider initialization"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, Any] = {
            "model_name": "text-embedding-ada-002",
            "api_key": "test-key",
            "api_base": "https://api.openai.com/v1",
            "timeout": 30,
            "dimensions": 1536,
        }

        _ = OpenAIEmbeddingProvider(config=config)

        # Test accessible attributes
        assert mock_embeddings.embedding_model is not None
        assert mock_embeddings._embeddings is not None

    @patch("langchain_llm_config.embeddings.providers.openai.OpenAIEmbeddings")
    def test_openai_embedding_provider_initialization_defaults(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test OpenAI embedding provider initialization with defaults"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {"model_name": "text-embedding-ada-002"}

        _ = OpenAIEmbeddingProvider(config=config)

        # Test accessible attributes
        assert mock_embeddings.embedding_model is not None

    @patch("langchain_llm_config.embeddings.providers.openai.OpenAIEmbeddings")
    def test_openai_embedding_provider_initialization_with_env_key(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test OpenAI embedding provider initialization using environment variable"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "text-embedding-ada-002",
            "api_key": "env-test-key",
        }

        _ = OpenAIEmbeddingProvider(config=config)

        # Verify OpenAIEmbeddings was called with the provided key
        mock_openai_embeddings.assert_called_once()
        call_args = mock_openai_embeddings.call_args
        assert call_args[1]["api_key"] == "env-test-key"

    @patch("langchain_llm_config.embeddings.providers.openai.OpenAIEmbeddings")
    def test_openai_embedding_provider_initialization_with_dummy_key(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """
        Test OpenAI embedding provider initialization with dummy key when no env var
        """
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "text-embedding-ada-002",
            "api_key": "dummy-key",
        }

        _ = OpenAIEmbeddingProvider(config=config)

        # Verify OpenAIEmbeddings was called with the provided key
        mock_openai_embeddings.assert_called_once()
        call_args = mock_openai_embeddings.call_args
        assert call_args[1]["api_key"] == "dummy-key"

    @patch("langchain_llm_config.embeddings.providers.openai.OpenAIEmbeddings")
    def test_openai_embedding_provider_embed_texts(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test OpenAI embedding provider embed_texts method"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {"model_name": "text-embedding-ada-002"}

        # Mock embedding results
        mock_embeddings.embed_documents.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]

        provider = OpenAIEmbeddingProvider(config=config)

        documents: List[str] = ["test document 1", "test document 2"]
        result = provider.embed_texts(documents)

        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_embeddings.embed_documents.assert_called_once_with(documents)

    @patch("langchain_llm_config.embeddings.providers.openai.OpenAIEmbeddings")
    def test_openai_embedding_provider_embed_texts_exception(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test OpenAI embedding provider embed_texts exception handling"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {"model_name": "text-embedding-ada-002"}

        mock_embeddings.embed_documents.side_effect = Exception("Embedding error")

        provider = OpenAIEmbeddingProvider(config=config)

        with pytest.raises(Exception, match="嵌入文本失败: Embedding error"):
            provider.embed_texts(["test document"])


class TestVLLMEmbeddingProvider:
    """Test VLLM embedding provider"""

    @patch("langchain_llm_config.embeddings.providers.vllm.OpenAIEmbeddings")
    def test_vllm_embedding_provider_initialization(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test VLLM embedding provider initialization"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, Any] = {
            "model_name": "bge-m3",
            "api_base": "http://localhost:8000/v1",
            "api_key": "test-key",
            "timeout": 30,
            "dimensions": 1024,
        }

        _ = VLLMEmbeddingProvider(config=config)

        # Test accessible attributes
        assert mock_embeddings.embedding_model is not None
        assert mock_embeddings._embeddings is not None

    @patch("langchain_llm_config.embeddings.providers.vllm.OpenAIEmbeddings")
    def test_vllm_embedding_provider_initialization_defaults(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test VLLM embedding provider initialization with defaults"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "bge-m3",
            "api_base": "http://localhost:8000/v1",
        }

        _ = VLLMEmbeddingProvider(config=config)

        # Test accessible attributes
        assert mock_embeddings.embedding_model is not None

    @patch("langchain_llm_config.embeddings.providers.vllm.OpenAIEmbeddings")
    def test_vllm_embedding_provider_embed_texts(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test VLLM embedding provider embed_texts method"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "bge-m3",
            "api_base": "http://localhost:8000/v1",
        }

        # Mock embedding results
        mock_embeddings.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

        provider = VLLMEmbeddingProvider(config=config)

        documents: List[str] = ["test document 1", "test document 2"]
        result = provider.embed_texts(documents)

        assert result == [[0.1, 0.2], [0.3, 0.4]]
        mock_embeddings.embed_documents.assert_called_once_with(documents)

    @patch("langchain_llm_config.embeddings.providers.vllm.OpenAIEmbeddings")
    def test_vllm_embedding_provider_embed_texts_exception(
        self, mock_openai_embeddings: MagicMock
    ) -> None:
        """Test VLLM embedding provider embed_texts exception handling"""
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "bge-m3",
            "api_base": "http://localhost:8000/v1",
        }

        mock_embeddings.embed_documents.side_effect = Exception("VLLM embedding error")

        provider = VLLMEmbeddingProvider(config=config)

        with pytest.raises(Exception, match="VLLM嵌入文本失败: VLLM embedding error"):
            provider.embed_texts(["test document"])


class TestInfinityEmbeddingProvider:
    """Test Infinity embedding provider"""

    @patch(
        "langchain_llm_config.embeddings.providers.infinity.LangchainInfinityEmbeddings"
    )
    def test_infinity_embedding_provider_initialization(
        self, mock_infinity_embeddings: MagicMock
    ) -> None:
        """Test Infinity embedding provider initialization"""
        mock_embeddings = MagicMock()
        mock_infinity_embeddings.return_value = mock_embeddings

        config: Dict[str, Any] = {
            "model_name": "models/bge-m3",
            "api_base": "http://localhost:7997/v1",
            "timeout": 30,
        }

        _ = InfinityEmbeddingProvider(config=config)

        # Test accessible attributes
        assert mock_embeddings.embedding_model is not None
        assert mock_embeddings._embeddings is not None

        # Verify LangchainInfinityEmbeddings was called with correct parameters
        mock_infinity_embeddings.assert_called_once()
        call_args = mock_infinity_embeddings.call_args
        assert call_args[1]["model"] == "models/bge-m3"
        assert call_args[1]["infinity_api_url"] == "http://localhost:7997/v1"

    @patch(
        "langchain_llm_config.embeddings.providers.infinity.LangchainInfinityEmbeddings"
    )
    def test_infinity_embedding_provider_initialization_defaults(
        self, mock_infinity_embeddings: MagicMock
    ) -> None:
        """Test Infinity embedding provider initialization with defaults"""
        mock_embeddings = MagicMock()
        mock_infinity_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "models/bge-m3",
            "api_base": "http://localhost:7997/v1",
        }

        _ = InfinityEmbeddingProvider(config=config)

        # Test accessible attributes
        assert mock_embeddings.embedding_model is not None

    @patch(
        "langchain_llm_config.embeddings.providers.infinity.LangchainInfinityEmbeddings"
    )
    def test_infinity_embedding_provider_embed_texts(
        self, mock_infinity_embeddings: MagicMock
    ) -> None:
        """Test Infinity embedding provider embed_texts method"""
        mock_embeddings = MagicMock()
        mock_infinity_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "models/bge-m3",
            "api_base": "http://localhost:7997/v1",
        }

        # Mock embedding results
        mock_embeddings.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

        provider = InfinityEmbeddingProvider(config=config)

        documents: List[str] = ["test document 1", "test document 2"]
        result = provider.embed_texts(documents)

        assert result == [[0.1, 0.2], [0.3, 0.4]]
        mock_embeddings.embed_documents.assert_called_once_with(documents)

    @patch(
        "langchain_llm_config.embeddings.providers.infinity.LangchainInfinityEmbeddings"
    )
    def test_infinity_embedding_provider_embed_texts_exception(
        self, mock_infinity_embeddings: MagicMock
    ) -> None:
        """Test Infinity embedding provider embed_texts exception handling"""
        mock_embeddings = MagicMock()
        mock_infinity_embeddings.return_value = mock_embeddings

        config: Dict[str, str] = {
            "model_name": "models/bge-m3",
            "api_base": "http://localhost:7997/v1",
        }

        mock_embeddings.embed_documents.side_effect = Exception(
            "Infinity embedding error"
        )

        provider = InfinityEmbeddingProvider(config=config)

        with pytest.raises(Exception, match="嵌入文本失败: Infinity embedding error"):
            provider.embed_texts(["test document"])
