from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from ..base import Assistant


class VLLMAssistant(Assistant):
    """VLLM助手实现（使用OpenAI兼容接口）"""

    def __init__(
        self,
        config: Dict[str, Any],
        response_model: Optional[Type[BaseModel]] = None,
        system_prompt: Optional[str] = None,
        auto_apply_parser: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        初始化VLLM助手

        Args:
            config: 配置字典
            response_model: 响应模型类（当auto_apply_parser=False时可选）
            system_prompt: 系统提示
            auto_apply_parser: 是否自动应用解析器（默认True，保持向后兼容）
            **kwargs: 额外参数
        """
        # 保存config作为实例变量，但不传递给父类
        self.config = config

        # 从config中提取需要的参数传递给父类，但不传递config本身
        super().__init__(
            model_name=config["model_name"],
            response_model=response_model,
            temperature=config.get("temperature", 0.6),
            max_tokens=config.get("max_tokens", 8192),
            base_url=config["api_base"],
            api_key=config.get("api_key", "EMPTY"),
            top_p=config.get("top_p", 0.8),
            connect_timeout=config.get("connect_timeout", 30),
            read_timeout=config.get("read_timeout", 60),
            model_kwargs=config.get("model_kwargs", {}),
            system_prompt=system_prompt,
            auto_apply_parser=auto_apply_parser,
            **kwargs,  # 传递其他参数
        )
