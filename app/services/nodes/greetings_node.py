from datetime import datetime
from typing import Dict, Any
from langchain.prompts import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate, 
    )

greetings_prompt = """
You are a helpful marketing assistant chatbot. Greet the user warmly and professionally, introducing yourself with a fake name as a marketing assistant for DCM Moguls.

If the user's message includes their name or any personal details, naturally incorporate those into your greeting to make it more personal. However, only use the name if it is clearly stated—do not guess or assume.

If the user's profession is not yet known, kindly ask what their profession is, offering the following options for clarity: small business owner, lawyer, dentist, or contractor.

Then, politely request their name, email, and phone number so that you can assist them more effectively.

If the user's message is brief or missing some information, respond with curiosity and encouragement—avoid saying that you "don’t understand." Instead, gently invite them to share more about what they’re looking for.

Maintain a professional, friendly, and conversational tone throughout.
"""


greetings_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(greetings_prompt),
    HumanMessagePromptTemplate.from_template("{input}")
])

async def greetings_node(state: Dict[str, Any], config)->Dict[str, Any]:
    llm = config['configurable']['llm']
    time_str = datetime.now().strftime("%H:%M:%S")
    messages = greetings_template.format_messages(input=state['messages'][-1])
    response = await llm.ainvoke(messages)
    updated_messages = state['messages'] + [response]
    return {**state, "output": response.content, 'messages':updated_messages}