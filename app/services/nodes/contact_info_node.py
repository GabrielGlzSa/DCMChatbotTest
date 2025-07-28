
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from app.core.logger import logger


        


system_template = (
    """You are a helpful and professional assistant for a company that provides personalized services based on the client's profession.

Known information:
{known}

Missing information:
{missing}

Instructions:
- If the profession is missing, explain that it is essential to know the client’s profession to offer relevant services.
- If the profession is known, thank the user for providing it.
- For any other missing fields (e.g., name, email), kindly ask the user to provide them.
- Be polite, professional, and concise.
- Do not assume any missing information.
- Always encourage the user to reply with any missing details."""
)


human_template = "{user_message}"

prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template),
])

# Node function
async def contact_info_node(state: Dict[str, Any], config) -> Dict[str, Any]:
    llm = config["configurable"]["llm"]
    input_msg = state["messages"][-1].content  # Most recent user message
    success = False

    # Extract current known values from state
    name = state.get("customer_name")
    profession = state.get("customer_profession")
    email = state.get("customer_email")

    # Build custom summary of known and missing fields
    known = []
    missing = []

    if name:
        known.append(f"name: {name}")
    else:
        missing.append("name")
    if profession:
        known.append(f"profession: {profession}")
    else:
        missing.append("profession")
    if email:
        known.append(f"email: {email}")
    else:
        missing.append("email")

    logger.debug(f"Known fields: {known}, Missing fields: {missing}")

    prompt = prompt_template.format_messages(
    known=known,
    missing=missing,
    user_message=input_msg
)   
    logger.debug(f"Prompt for LLM:\n{prompt}")
    
    llm_response = await llm.ainvoke(prompt)
    logger.debug(f"LLM response:\n{llm_response.content}")

    # Update message history
    updated_messages = state["messages"] + [llm_response]

    
    return {
        "messages": updated_messages
    }