from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .models import ProgressItemStatus, ToolResponse


def update_progress_info(
    ctx: CallbackContext,
    key: str,
    status: ProgressItemStatus = ProgressItemStatus.RUNNING,
) -> None:
    progress_info = ctx.state.get("progress_info") or {}
    progress_info[key] = status
    ctx.state["progress_info"] = progress_info


def reset_progress_info(ctx: CallbackContext, key: str | None = None) -> None:
    progress_info = ctx.state.get("progress_info")
    if key and progress_info:
        progress_info.pop(key, None)
        ctx.state["progress_info"] = progress_info
    else:
        ctx.state["progress_info"] = None


def update_state_if_necessary(ctx: CallbackContext, delta: dict[str, Any]) -> None:
    for key, value in delta.items():
        if ctx.state.get(key) != value:
            ctx.state[key] = value


def find_approved_resource_in(content: types.Content | None) -> dict[str, Any] | None:
    if not (content and content.parts):
        return None
    for part in content.parts:
        if part.function_response and part.function_response.response:
            result = ToolResponse[dict[str, Any]](
                **part.function_response.response
            ).get("result")
            if result and result.get("resource"):
                return result.get("resource")

    return None
