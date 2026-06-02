from google.adk.tools import FunctionTool


def transfer_to(agent_name: str) -> str:
    """Transfer the conversation to another agent. Only call this AFTER the user explicitly confirms they want to be transferred."""
    return f"Transfer to {agent_name} initiated. Say a brief goodbye."


def end_conversation() -> str:
    """Call this when the conversation is complete and the customer has been fully served."""
    return "Conversation ended."


_transfer_tool = FunctionTool(transfer_to)
_end_tool = FunctionTool(end_conversation)
