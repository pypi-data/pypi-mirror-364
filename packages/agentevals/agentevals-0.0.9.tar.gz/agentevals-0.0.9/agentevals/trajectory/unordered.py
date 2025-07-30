from __future__ import annotations
from warnings import warn

from agentevals.types import (
    ChatCompletionMessage,
    ToolArgsMatchMode,
    ToolArgsMatchOverrides,
)
from agentevals.trajectory.utils import (
    _is_trajectory_superset,
    _normalize_to_openai_messages_list,
)
from agentevals.utils import _run_evaluator, _arun_evaluator

from typing import Any, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage


def _scorer(
    *,
    outputs: list[ChatCompletionMessage],
    reference_outputs: list[ChatCompletionMessage],
    tool_args_match_mode: ToolArgsMatchMode,
    tool_args_match_overrides: Optional[ToolArgsMatchOverrides] = None,
    **kwargs: Any,
):
    if outputs is None or reference_outputs is None:
        raise ValueError(
            "Trajectory unordered match requires both outputs and reference_outputs"
        )
    unordered_match = _is_trajectory_superset(
        outputs, reference_outputs, tool_args_match_mode, tool_args_match_overrides
    ) and _is_trajectory_superset(
        reference_outputs, outputs, tool_args_match_mode, tool_args_match_overrides
    )
    return unordered_match


def trajectory_unordered_match(
    *,
    outputs: Union[list[ChatCompletionMessage], list[BaseMessage], dict],
    reference_outputs: Union[list[ChatCompletionMessage], list[BaseMessage], dict],
    **kwargs: Any,
):
    """
    DEPRECATED: Use create_trajectory_match_evaluator() instead:
    ```python
    from agentevals.trajectory.match import create_trajectory_match_evaluator
    evaluator = create_trajectory_match_evaluator(trajectory_match_mode="unordered")
    evaluator(outputs=outputs, reference_outputs=reference_outputs)
    ```

    Evaluate whether an input agent trajectory and called tools contains all the tools used in a reference trajectory.
    This accounts for some differences in an LLM's reasoning process in a case-by-case basis.

    Args:
        outputs (Union[list[ChatCompletionMessage], list[BaseMessage], dict]): Actual trajectory the agent followed.
            May be a list of OpenAI messages, a list of LangChain messages, or a dictionary containing
            a "messages" key with one of the above.
        reference_outputs (Union[list[ChatCompletionMessage], list[BaseMessage], dict]): Ideal reference trajectory the agent should have followed.
            May be a list of OpenAI messages, a list of LangChain messages, or a dictionary containing
            a "messages" key with one of the above.

    Returns:
        EvaluatorResult: Contains a score of True if trajectory matches, False otherwise
    """
    warn(
        "trajectory_unordered_match() is deprecated. Use create_trajectory_match_evaluator(trajectory_match_mode='unordered') instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    outputs = _normalize_to_openai_messages_list(outputs)
    reference_outputs = _normalize_to_openai_messages_list(reference_outputs)

    return _run_evaluator(
        run_name="trajectory_unordered_match",
        scorer=_scorer,
        feedback_key="trajectory_unordered_match",
        outputs=outputs,
        reference_outputs=reference_outputs,
        tool_args_match_mode="ignore",
        **kwargs,
    )


async def trajectory_unordered_match_async(
    *,
    outputs: Union[list[ChatCompletionMessage], list[BaseMessage], dict],
    reference_outputs: Union[list[ChatCompletionMessage], list[BaseMessage], dict],
    **kwargs: Any,
):
    """
    Evaluate whether an input agent trajectory and called tools contains all the tools used in a reference trajectory.
    This accounts for some differences in an LLM's reasoning process in a case-by-case basis.

    Args:
        outputs (Union[list[ChatCompletionMessage], list[BaseMessage], dict]): Actual trajectory the agent followed.
            May be a list of OpenAI messages, a list of LangChain messages, or a dictionary containing
            a "messages" key with one of the above.
        reference_outputs (Union[list[ChatCompletionMessage], list[BaseMessage], dict]): Ideal reference trajectory the agent should have followed.
            May be a list of OpenAI messages, a list of LangChain messages, or a dictionary containing
            a "messages" key with one of the above.

    Returns:
        EvaluatorResult: Contains a score of True if trajectory matches, False otherwise
    """
    warn(
        "trajectory_unordered_match_async() is deprecated. Use create_async_trajectory_match_evaluator(trajectory_match_mode='unordered') instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    outputs = _normalize_to_openai_messages_list(outputs)
    reference_outputs = _normalize_to_openai_messages_list(reference_outputs)

    return await _arun_evaluator(
        run_name="trajectory_unordered_match",
        scorer=_scorer,
        feedback_key="trajectory_unordered_match",
        outputs=outputs,
        reference_outputs=reference_outputs,
        tool_args_match_mode="ignore",
        **kwargs,
    )
