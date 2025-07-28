from typing import Dict, Any
from langchain.prompts import PromptTemplate

from app.core.logger import logger


# Prompt to answer based on context
context_prompt = PromptTemplate.from_template("""You are a knowledgeable and professional assistant for DCM Moguls, a marketing company dedicated to helping clients grow their businesses. Use the information provided below to confidently and directly answer the user's question.

When responding:
- Do not mention that you are referencing or reviewing context.
- If the context includes links, include them in your response when relevant.
- If the answer cannot be found in the context, politely say you're not certain and will forward the question to a team member at DCM Moguls for personalized assistance.

Always maintain a warm, helpful, and brand-aligned tone in your responses.

Context:
{context}

Question:
{question}
""")

async def retrieve_and_respond_node(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    retriever = config["configurable"]["retriever"]
    llm = config["configurable"]["llm"]

    query = state["messages"][-1].content + f" I am a {state['customer_profession']}."

    # 1. Retrieve documents
    docs = retriever.get_relevant_documents(query)
    retrieved_text = "\n\n".join(doc.page_content for doc in docs)

    logger.info(f"Retrieved {len(docs)} documents for query: {query}")
    logger.debug(f"Retrieved text: {retrieved_text}...") 
    # 2. Format the prompt
    prompt = context_prompt.format(context=retrieved_text, question=query)

    # 3. Generate the answer
    response = await llm.ainvoke(prompt)

    # 4. Update the state
    updated_messages = state["messages"] + [response]

    return {
        "messages": updated_messages
    }