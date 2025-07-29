import os
from typing import Any, Dict, Optional, Type, Union

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr

from ..base import Assistant


class GeminiAssistant(Assistant):
    """Gemini model assistant implementation."""

    def __init__(
        self,
        config: Dict[str, Any],
        response_model: Optional[Type[BaseModel]] = None,
        system_prompt: Optional[str] = None,
        auto_apply_parser: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        初始化Gemini助手

        Args:
            config: 配置字典
            response_model: 响应模型类（当auto_apply_parser=False时可选）
            system_prompt: 系统提示
            auto_apply_parser: 是否自动应用解析器（默认True，保持向后兼容）
            **kwargs: 额外参数
        """
        # Validate parameters
        if auto_apply_parser and response_model is None:
            raise ValueError(
                "response_model is required when auto_apply_parser=True. "
                "Either provide a response_model or set auto_apply_parser=False "
                "for raw text output."
            )

        # 保存config作为实例变量，但不传递给父类
        self.config = config

        # 设置系统提示和响应模型
        self.system_prompt = system_prompt
        self.response_model = response_model
        self.auto_apply_parser = auto_apply_parser

        # Initialize parser as None with proper type annotation
        self.parser: Optional[Runnable[Union[BaseMessage, str], Any]] = None

        # 从config中提取参数
        model_name = config["model_name"]
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)
        api_key = config.get("api_key")
        top_p = config.get("top_p", 1.0)
        connect_timeout = config.get("connect_timeout", 30)
        model_kwargs = config.get("model_kwargs", {})

        # Ensure model_kwargs is a dictionary
        if model_kwargs is None:
            model_kwargs = {}

        # Add model-specific parameters to model_kwargs
        if max_tokens is not None:
            model_kwargs["max_output_tokens"] = max_tokens
        if top_p is not None:
            model_kwargs["top_p"] = top_p

        # 初始化Gemini LLM with only top-level accepted parameters
        self.llm: Any = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(
                api_key or os.getenv("GEMINI_API_KEY", "dummy-key") or ""
            ),
            timeout=float(connect_timeout) if connect_timeout else None,
            **model_kwargs,
        )

        # 设置提示模板和处理链
        self._setup_prompt_and_chain()

        # 根据参数决定是否自动应用解析器（向后兼容）
        if auto_apply_parser:
            self.apply_parser()

    def _setup_prompt_and_chain(self) -> None:
        """设置提示模板和处理链"""
        if self.response_model is not None:
            # 创建基础解析器（仅当有response_model时）
            base_parser = PydanticOutputParser(pydantic_object=self.response_model)

            # 获取格式说明
            format_instructions = base_parser.get_format_instructions()
            escaped_format_instructions = format_instructions.replace(
                "{", "{{"
            ).replace("}", "}}")

            # 创建带重试的解析器
            self.parser = base_parser.with_retry(
                stop_after_attempt=3,
                retry_if_exception_type=(ValueError, KeyError),
            )

            # 创建结构化提示模板（用于JSON输出）
            self.prompt = PromptTemplate(
                template=(
                    "{system_prompt}\n"
                    "请严格按照以下格式提供您的回答。您的回答必须：\n"
                    "1. 完全符合指定的JSON格式\n"
                    "2. 不要添加任何额外的解释或注释\n"
                    "3. 对于有默认值的字段（如intension、language），如果不知道具体值，"
                    "请直接省略该字段，不要使用null\n"
                    "4. 对于没有默认值的可选字段，如果确实没有值，才使用null\n"
                    "5. 必须使用标准ASCII字符作为JSON语法（如 : 而不是 ：）\n"
                    "格式要求：\n"
                    "{format_instructions}\n\n"
                    "{context}\n"
                    "用户: {question}\n"
                    "助手:"
                ),
                input_variables=["question", "system_prompt", "context"],
                partial_variables={"format_instructions": escaped_format_instructions},
            )
        else:
            # 没有response_model时，使用简单的提示模板（用于原始文本输出）
            self.parser = None
            self.prompt = PromptTemplate(
                template=(
                    "{system_prompt}\n" "{context}\n" "用户: {question}\n" "助手:"
                ),
                input_variables=["question", "system_prompt", "context"],
            )

        # 构建基础链（不包含解析器）
        from langchain_core.runnables import Runnable

        self.base_chain: Runnable = RunnablePassthrough() | self.prompt | self.llm

        # 初始化时使用基础链
        self.chain: Runnable = self.base_chain

    def apply_parser(self, response_model: Optional[Type[BaseModel]] = None) -> None:
        """
        应用解析器到链上，使输出结构化

        Args:
            response_model: 可选的响应模型类。如果提供，将创建新的解析器；
                          如果不提供，将使用现有的解析器（如果存在）

        调用此方法后，ask方法将返回解析后的结构化数据

        Raises:
            ValueError: 当没有response_model且没有现有解析器时
        """
        if response_model is not None:
            # 创建新的解析器
            base_parser = PydanticOutputParser(pydantic_object=response_model)
            self.parser = base_parser.with_retry(
                stop_after_attempt=3,
                retry_if_exception_type=(ValueError, KeyError),
            )
            # 更新response_model
            self.response_model = response_model

            # 重新设置提示模板以包含格式说明
            self._setup_prompt_and_chain()
        elif self.parser is None:
            raise ValueError(
                "Cannot apply parser: no response_model was provided during "
                "initialization and none was passed to apply_parser(). "
                "Either provide a response_model parameter or create the "
                "assistant with a response_model."
            )

        # 应用解析器到链
        # At this point, self.parser is guaranteed to be non-None
        assert self.parser is not None
        self.chain = self.base_chain | self.parser

    def ask(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        处理用户查询并返回结构化响应（同步版本）

        Args:
            query: 用户查询文本
            extra_system_prompt: 额外的系统提示
            context: 可选的上下文信息
            **kwargs: 额外参数

        Returns:
            解析并验证后的结构化响应

        Raises:
            ValueError: 当处理查询时发生错误
        """
        try:
            # 构建系统提示
            system_prompt = self.system_prompt or ""
            if extra_system_prompt:
                system_prompt = (
                    f"{system_prompt}\n{extra_system_prompt}"
                    if system_prompt
                    else extra_system_prompt
                )

            # 构建上下文信息
            context_str = f"背景信息：{context}" if context else ""

            # 获取输出
            output = self.chain.invoke(
                {
                    "question": query,
                    "system_prompt": system_prompt,
                    "context": context_str,
                }
            )

            # 检查是否应用了解析器（通过检查解析器状态而不是输出类型）
            if self.parser is not None and hasattr(output, "model_dump"):
                # 解析器已应用，返回结构化数据
                result: Dict[str, Any] = output.model_dump()
                return result
            else:
                # 解析器未应用，返回原始LLM输出的文本内容
                if hasattr(output, "content"):
                    content = output.content
                    # Ensure we return a string, not another object
                    return str(content) if content is not None else ""
                else:
                    return str(output)

        except Exception as e:
            raise ValueError(f"处理查询时出错: {str(e)}") from e

    async def ask_async(
        self,
        query: str,
        extra_system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], str]:
        """
        处理用户查询并返回结构化响应（异步版本）

        Args:
            query: 用户查询文本
            extra_system_prompt: 额外的系统提示
            context: 可选的上下文信息
            **kwargs: 额外参数

        Returns:
            解析并验证后的结构化响应

        Raises:
            ValueError: 当处理查询时发生错误
        """
        try:
            # 构建系统提示
            system_prompt = self.system_prompt or ""
            if extra_system_prompt:
                system_prompt = (
                    f"{system_prompt}\n{extra_system_prompt}"
                    if system_prompt
                    else extra_system_prompt
                )

            # 构建上下文信息
            context_str = f"背景信息：{context}" if context else ""

            # 获取输出
            output = await self.chain.ainvoke(
                {
                    "question": query,
                    "system_prompt": system_prompt,
                    "context": context_str,
                }
            )

            # 检查是否应用了解析器（通过检查解析器状态而不是输出类型）
            if self.parser is not None and hasattr(output, "model_dump"):
                # 解析器已应用，返回结构化数据
                result: Dict[str, Any] = output.model_dump()
                return result
            else:
                # 解析器未应用，返回原始LLM输出的文本内容
                if hasattr(output, "content"):
                    content = output.content
                    # Ensure we return a string, not another object
                    return str(content) if content is not None else ""
                else:
                    return str(output)

        except Exception as e:
            raise ValueError(f"处理查询时出错: {str(e)}") from e
