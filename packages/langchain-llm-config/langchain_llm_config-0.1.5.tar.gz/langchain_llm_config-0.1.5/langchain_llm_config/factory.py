from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel

from .assistant.base import Assistant
from .assistant.chat_streaming import ChatStreaming
from .assistant.providers.gemini import GeminiAssistant
from .assistant.providers.vllm import VLLMAssistant
from .config import load_config
from .embeddings.base import BaseEmbeddingProvider
from .embeddings.providers.gemini import GeminiEmbeddingProvider
from .embeddings.providers.infinity import InfinityEmbeddingProvider
from .embeddings.providers.openai import OpenAIEmbeddingProvider
from .embeddings.providers.vllm import VLLMEmbeddingProvider

# 助手提供者映射
_ASSISTANT_PROVIDERS = {
    "vllm": VLLMAssistant,
    "openai": Assistant,
    "gemini": GeminiAssistant,
}

# Type alias for concrete embedding providers
EmbeddingProviderType = Union[
    OpenAIEmbeddingProvider,
    InfinityEmbeddingProvider,
    VLLMEmbeddingProvider,
    GeminiEmbeddingProvider,
]

# 嵌入提供者映射
_EMBEDDING_PROVIDERS: Dict[str, Type[EmbeddingProviderType]] = {
    "openai": OpenAIEmbeddingProvider,
    "infinity": InfinityEmbeddingProvider,
    "vllm": VLLMEmbeddingProvider,
    "gemini": GeminiEmbeddingProvider,
}


def create_assistant(
    response_model: Optional[Type[BaseModel]] = None,
    provider: Optional[str] = None,
    system_prompt: Optional[str] = None,
    config_path: Optional[str] = None,
    auto_apply_parser: bool = True,
    **kwargs: Any,
) -> Any:
    """
    创建助手实例

    Args:
        response_model: 响应模型类（当auto_apply_parser=False时可选）
        provider: 提供者名称，默认使用配置中的默认值
        system_prompt: 系统提示
        config_path: 配置文件路径
        auto_apply_parser: 是否自动应用解析器（默认True，保持向后兼容）
        **kwargs: 额外参数

    Returns:
        配置好的助手实例

    Raises:
        ValueError: 当auto_apply_parser=True但未提供response_model时
    """
    # Validate parameters
    if auto_apply_parser and response_model is None:
        raise ValueError(
            "response_model is required when auto_apply_parser=True. "
            "Either provide a response_model or set auto_apply_parser=False "
            "for raw text output."
        )

    config = load_config(config_path)

    if provider is None:
        provider = config["default"]["chat_provider"]

    # Regular assistant creation
    if provider not in _ASSISTANT_PROVIDERS:
        raise ValueError(f"未知的助手提供者: {provider}")

    provider_class = _ASSISTANT_PROVIDERS[provider]
    provider_config = config[provider]["chat"]

    # 根据不同的提供者类型，传递不同的参数
    if provider == "openai":
        # 对于OpenAI，直接传递各个参数，而不是config对象
        return provider_class(
            model_name=provider_config["model_name"],
            response_model=response_model,
            temperature=provider_config.get("temperature", 0.7),
            max_tokens=provider_config.get("max_tokens", 2000),
            base_url=provider_config.get("api_base"),
            api_key=provider_config.get("api_key"),
            top_p=provider_config.get("top_p", 1.0),
            read_timeout=provider_config.get("read_timeout"),
            connect_timeout=provider_config.get("connect_timeout"),
            model_kwargs=provider_config.get("model_kwargs", {}),
            system_prompt=system_prompt,
            auto_apply_parser=auto_apply_parser,
            **kwargs,
        )
    elif provider == "gemini":
        # 对于Gemini，传递config对象
        return provider_class(
            config=provider_config,
            response_model=response_model,
            system_prompt=system_prompt,
            auto_apply_parser=auto_apply_parser,
            **kwargs,
        )
    else:
        # 对于其他提供者如VLLM，传递config对象
        return provider_class(
            config=provider_config,
            response_model=response_model,
            system_prompt=system_prompt,
            auto_apply_parser=auto_apply_parser,
            **kwargs,
        )


def create_chat_streaming(
    provider: Optional[str] = None,
    system_prompt: Optional[str] = None,
    config_path: Optional[str] = None,
    **kwargs: Any,
) -> ChatStreaming:
    """
    创建纯流式聊天助手实例（无响应模型约束）

    Args:
        provider: 提供者名称，默认使用配置中的默认值
        system_prompt: 系统提示
        config_path: 配置文件路径
        **kwargs: 额外参数

    Returns:
        配置好的流式聊天助手实例
    """
    config = load_config(config_path)

    if provider is None:
        provider = config["default"]["chat_provider"]

    # Type assertion to help type checker
    assert provider is not None
    provider_config = config[provider]["chat"]

    return ChatStreaming(
        model_name=provider_config["model_name"],
        temperature=provider_config.get("temperature", 0.7),
        max_tokens=provider_config.get("max_tokens", 2000),
        base_url=provider_config.get("api_base"),
        api_key=provider_config.get("api_key"),
        top_p=provider_config.get("top_p", 1.0),
        read_timeout=provider_config.get("read_timeout"),
        connect_timeout=provider_config.get("connect_timeout"),
        model_kwargs=provider_config.get("model_kwargs", {}),
        system_prompt=system_prompt,
        **kwargs,
    )


def create_embedding_provider(
    provider: Optional[str] = None, config_path: Optional[str] = None, **kwargs: Any
) -> EmbeddingProviderType:
    """
    创建嵌入提供者实例

    Args:
        provider: 提供者名称，默认使用配置中的默认值
        config_path: 配置文件路径
        **kwargs: 额外参数

    Returns:
        配置好的嵌入提供者实例
    """
    config = load_config(config_path)

    if provider is None:
        provider = config["default"]["embedding_provider"]

    if provider not in _EMBEDDING_PROVIDERS:
        raise ValueError(f"未知的嵌入提供者: {provider}")

    provider_class: Type[EmbeddingProviderType] = _EMBEDDING_PROVIDERS[provider]

    return provider_class(config=config[provider]["embeddings"], **kwargs)
