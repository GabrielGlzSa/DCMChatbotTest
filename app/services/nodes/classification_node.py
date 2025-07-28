import pandas as pd
from typing import Dict, Any

from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

from app.core.logger import logger
from app.core.embeddings import get_embedding_function

fs_class_examples = pd.read_csv("./app/data/few_shot_examples/classification.csv").to_dict(orient="records")

# Create chroma for few shot examples for msg classification.
embedding_function = get_embedding_function()
db_class = Chroma(collection_name="msg_class_examples", embedding_function=embedding_function)
db_class.add_texts([e["input"] for e in fs_class_examples], metadatas=fs_class_examples)

# Few shot example selector for shopping message classification.
class_example_selector = SemanticSimilarityExampleSelector(
    vectorstore=db_class,
    k=5
)

class_prompt = """You are a helpful assistant for a marketing agency chatbot.

Your task is to classify incoming user messages into one of the following intent categories:

- greeting: Simple greetings like "hi", "hello", "good morning".
- services: User expresses interest in growing their business, marketing services, or customer acquisition.
- contact_info: The user provides their name, email address, or phone number.
- spam: The message doesn’t match any known category (e.g., emojis, unrelated content).

Use only one intent per message. If the message includes multiple things, choose the one that reflects the **primary purpose** of the message.


Below are examples of messages and their intent class.

"""

suffix_class = """Classify the following message:

Message: {input}
Intent:
"""
# Few shot prompt for message classification.
fs_prompt_msg_class = FewShotPromptTemplate(
    example_selector=class_example_selector,
    example_prompt=PromptTemplate(
        input_variables=["input", "class"],
        template="Message: {input}\n{class}"
    ),
    prefix=class_prompt,
    suffix=suffix_class,
    input_variables=["input"]
)

async def classification_node(state:Dict[str, Any], config)->Dict[str, Any]:
    """
    Classifies the input text into categories.
    """
    llm = config['configurable']['llm']
    llm_prompt = fs_prompt_msg_class.format(input=state['messages'][-1].content)
    logger.debug(f'LLM prompt:\n{llm_prompt}')
    llm_response = await llm.ainvoke(llm_prompt)
    llm_response_text = llm_response.content.strip().lower()
    logger.info(f'Model response:\n{llm_response_text}')
    if 'greeting_or_profession' in llm_response_text:
        msg_type = "greeting_or_profession"
    elif 'services' in llm_response_text:
        msg_type = "services"
    elif 'contact_info' in llm_response_text:
        msg_type = "contact_info"
    elif 'faq' in llm_response_text:
        msg_type = "faq"
    elif 'generic_greeting' in llm_response_text:
        msg_type = "generic_greeting"
    else:
        msg_type = "unknown"
    return {'msg_type': msg_type}