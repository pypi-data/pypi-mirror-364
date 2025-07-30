from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4, UUID

import tiktoken
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from langchain.schema.messages import BaseMessage


class AbstractMonitorCore(BaseCallbackHandler, ABC):
    """LangChain 组件监控抽象基类，提供标准化的日志记录和监控功能。

    该类定义了监控 LangChain 各组件（LLM、Chain、Tool）执行过程的标准接口，
    子类需实现 _db_operations 方法以完成日志数据的持久化存储。
    """

    def __init__(
        self, thread_id: str | None = None, token_model_name: str = "gpt-3.5-turbo"
    ) -> None:
        """初始化监控器核心实例。

        Args:
            thread_id (str | None): 线程/协程标识符，用于区分不同执行上下文。
                                      如果未提供，则自动生成一个新的 UUID。
            token_model_name (str): 用于 token 计数的模型名称，默认为 "gpt-3.5-turbo"。
                                   必须与 tiktoken 支持的模型名称一致。
        """
        self.thread_id = thread_id or uuid4()
        self.token_encoder = tiktoken.encoding_for_model(token_model_name)

    def _count_tokens(self, text: str | list[BaseMessage]) -> int:
        """计算输入内容的 token 数量。

        支持普通字符串和 LangChain 的 BaseMessage 列表（用于聊天模型）。

        Args:
            text (str | list[BaseMessage]): 要计算的内容，可以是字符串或消息列表。

        Returns:
            int: 计算得出的 token 数量。如果输入为空或无效，返回 0。
        """
        if isinstance(text, str):
            return len(self.token_encoder.encode(text))
        elif isinstance(text, list):
            return sum(
                len(self.token_encoder.encode(msg.content))
                for msg in text
                if hasattr(msg, "content")
            )
        return 0

    def _prepare_log_data(
        self,
        run_id: UUID,
        parent_run_id: UUID | None,
        event_type: Literal[
            "llm", "llm_error", "chain", "chain_error", "tool", "tool_error"
        ],
        event_name: str,
        input_data: Any,
        output_data: Any,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        """构造标准化的日志数据结构。

        将监控数据转换为统一的字典格式，包含 trace_id、时间戳、token 用量等标准字段。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            event_type (Literal): 事件类型标识，限定为预定义的几种组件类型。
            event_name (str): 组件名称（如模型名称、工具名称等）。
            input_data (Any): 输入数据，会自动转换为字符串格式。
            output_data (Any): 输出数据，会自动转换为字符串格式。
            metadata (dict | None): 附加的元数据字典。如果为 None 则使用空字典。

        Returns:
            dict[str, Any]: 包含以下字段的标准日志字典：
                - trace_id: 唯一追踪标识符（UUID）
                - run_id: 当前运行的唯一标识符（UUID）
                - thread_id: 线程/协程标识符
                - parent_run_id: 父运行的唯一标识符（UUID）
                - event_type: 事件类型
                - event_name: 组件名称
                - input_data: 输入内容（字符串格式）
                - output_data: 输出内容（字符串格式）
                - timestamp: ISO 8601 格式的时间戳
                - token_usage: 总 token 消耗量
                - metadata: 合并后的元数据字典
        """
        metadata = metadata or {}
        return {
            "trace_id": uuid4(),
            "run_id": run_id,
            "thread_id": self.thread_id,
            "parent_run_id": parent_run_id,
            "event_type": event_type,
            "event_name": event_name,
            "input_data": str(input_data),
            "output_data": str(output_data),
            "timestamp": datetime.now().isoformat(),
            "token_usage": (
                self._count_tokens(input_data) + self._count_tokens(output_data)
            ),
            "metadata": metadata,
        }

    @abstractmethod
    def _db_operations(self, log_data: dict[str, Any]) -> None:
        """数据库操作抽象方法（必须由子类实现）。

        定义如何将标准化日志数据持久化到存储系统（如数据库、文件等）。

        Args:
            log_data (dict[str, Any]): 由 _prepare_log_data 生成的标准化日志字典。

        Raises:
            NotImplementedError: 如果子类没有实现该方法。
        """
        raise NotImplementedError("_db_operations must be implemented in subclasses")

    # LLM 回调
    def on_llm_start(
        self,
        run_id: UUID,
        serialized: dict[str, Any],
        prompts: list[str],
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 开始处理时的回调方法。

        当语言模型开始处理输入提示时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            serialized (dict[str, Any]): 包含模型配置的序列化字典。
            prompts (list[str]): 输入的提示词列表。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm",
            event_name=serialized.get("name", "unknown_llm"),
            input_data=prompts,
            output_data="",
            metadata={
                **kwargs,
                "model": serialized.get("kwargs", {}).get("model_name"),
            },
        )
        self._db_operations(log_data)

    def on_llm_end(
        self,
        run_id: UUID,
        response: LLMResult,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 完成处理时的回调方法。

        当语言模型完成生成并返回结果时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            response (LLMResult): LLM 生成的结果对象。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm",
            event_name=kwargs.get("name", "unknown_llm"),
            input_data="",
            output_data=response,
            metadata=kwargs,
        )
        self._db_operations(log_data)

    def on_llm_error(
        self,
        run_id: UUID,
        error: BaseException,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """LLM 处理出错时的回调方法。

        当语言模型处理过程中发生异常时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            error (BaseException): 捕获的异常对象。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="llm_error",
            event_name=kwargs.get("name", "unknown_llm"),
            input_data="",
            output_data=error,
            metadata=kwargs,
        )
        self._db_operations(log_data)

    # Chain 回调
    def on_chain_start(
        self,
        run_id: UUID,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """执行链开始运行时的回调方法。

        当 Chain 组件开始处理输入时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            serialized (dict[str, Any]): 包含 Chain 配置的序列化字典。
            inputs (dict[str, Any]): Chain 的输入字典。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain",
            event_name=serialized.get("name", "unknown_chain"),
            input_data=inputs,
            output_data="",
            metadata=kwargs,
        )
        self._db_operations(log_data)

    def on_chain_end(
        self,
        run_id: UUID,
        outputs: dict[str, Any],
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """执行链完成运行时的回调方法。

        当 Chain 组件处理完成并返回输出时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            outputs (dict[str, Any]): Chain 的输出字典。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain",
            event_name=kwargs.get("name", "unknown_chain"),
            input_data="",
            output_data=outputs,
            metadata=kwargs,
        )
        self._db_operations(log_data)

    def on_chain_error(
        self,
        run_id: UUID,
        error: BaseException,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """执行链运行出错时的回调方法。

        当 Chain 组件处理过程中发生异常时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            error (BaseException): 捕获的异常对象。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="chain_error",
            event_name=kwargs.get("name", "unknown_chain"),
            input_data="",
            output_data=str(error),
            metadata=kwargs,
        )
        self._db_operations(log_data)

    # Tool 回调
    def on_tool_start(
        self,
        run_id: UUID,
        serialized: dict[str, Any],
        input_str: str,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """工具开始执行时的回调方法。

        当 Tool 组件开始处理输入时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            serialized (dict[str, Any]): 包含 Tool 配置的序列化字典。
            input_str (str): Tool 的输入字符串。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool",
            event_name=serialized.get("name", "unknown_tool"),
            input_data=input_str,
            output_data="",
            metadata={**kwargs, "tool_args": serialized.get("kwargs", {})},
        )
        self._db_operations(log_data)

    def on_tool_end(
        self,
        run_id: UUID,
        output: Any,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """工具完成执行时的回调方法。

        当 Tool 组件处理完成并返回输出时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            output (Any): Tool 的输出结果。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool",
            event_name=kwargs.get("name", "unknown_tool"),
            input_data="",
            output_data=str(output),
            metadata=kwargs,
        )
        self._db_operations(log_data)

    def on_tool_error(
        self,
        run_id: UUID,
        error: BaseException,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """工具执行出错时的回调方法。

        当 Tool 组件处理过程中发生异常时会触发此方法。

        Args:
            run_id (UUID): 当前运行的唯一标识符。
            error (BaseException): 捕获的异常对象。
            parent_run_id (UUID | None): 父运行的唯一标识符，如果没有则为 None。
            **kwargs: 其他运行时参数，会自动合并到 metadata 中。
        """
        log_data = self._prepare_log_data(
            run_id=run_id,
            parent_run_id=parent_run_id,
            event_type="tool_error",
            event_name=kwargs.get("name", "unknown_tool"),
            input_data="",
            output_data=str(error),
            metadata=kwargs,
        )
        self._db_operations(log_data)


__all__ = ["AbstractMonitorCore"]
