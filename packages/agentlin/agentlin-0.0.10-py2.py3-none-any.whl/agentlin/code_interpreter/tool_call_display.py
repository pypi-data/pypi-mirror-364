
from typing_extensions import Any

from agentlin.code_interpreter.types import MIME_TOOL_CALL, MIME_TOOL_RESPONSE, ToolCall, ToolResponse


# Try to import IPython components
try:
    from IPython.display import display
    from IPython.core.display import DisplayObject
    IPYTHON_AVAILABLE = True
except ImportError:
    # Create dummy classes for non-IPython environments
    class DisplayObject:
        def __init__(self, *args, **kwargs):
            pass

    def display(obj):
        """Fallback display function for non-IPython environments"""
        if hasattr(obj, '_repr_mimebundle_'):
            bundle = obj._repr_mimebundle_()
            if 'text/plain' in bundle:
                print(bundle['text/plain'])
            else:
                print(str(obj))
        else:
            print(str(obj))

    IPYTHON_AVAILABLE = False


def display_tool_response(
    message_content: list[dict[str, Any]],
    block_list: list[dict[str, Any]],
    **kwargs,
):
    """
    Display tool response data in Jupyter notebook

    Args:
        message_content: List of dictionaries containing tool response data
        block_list: List of dictionaries containing block information
        **kwargs: Additional keyword arguments
    """
    tool_response = ToolResponse(
        message_content=message_content,
        block_list=block_list,
        data=kwargs,
    )
    display({
        MIME_TOOL_RESPONSE: tool_response,
    })


def display_tool_call(
    tool_name: str,
    tool_args: dict[str, Any],
    call_id: str,
):
    """
    Display tool call information in Jupyter notebook

    Args:
        tool_name: Name of the tool being called
        tool_args: Arguments passed to the tool
        call_id: Unique identifier for the tool call
    """
    tool_call = ToolCall(
        type="tool_call",
        tool_name=tool_name,
        tool_args=tool_args,
        call_id=call_id,
    )
    display({
        MIME_TOOL_CALL: tool_call,
    })