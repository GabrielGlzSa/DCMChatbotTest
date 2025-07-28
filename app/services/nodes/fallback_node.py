from typing import Dict, Any
from langchain.schema.messages import AIMessage

fallback_message = lambda state: {state['messages'] + [AIMessage(
        content="I'm not sure how to help with that. Let me connect you with a human agent.")]}

async def fallback_node(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback node that handles unknown messages.
    """
    response = AIMessage(
        content="I'm only able to provide you with information about our services and frequently asked questions. I am unable to answer unrelated questions. If you need help with something else, please contact our support team."
    )
    updated_messages = state['messages'] + [response]
    return {**state, "output": response.content, 'messages': updated_messages}