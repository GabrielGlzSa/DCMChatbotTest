from langchain_core.messages import HumanMessage

from uuid import uuid4
from time import perf_counter
from app.services.graph import build_chatbot_graph
from app.core.qdrant_database import get_qdrant_retriever
from app.core.logger import logger
from app.core.llm import get_llm


# Move this to database for persistance.
customer_threads = {}

SESSION_STATE = {}

graph = build_chatbot_graph()

def get_or_create_thread_id(customer_id: int) -> str:
    if customer_id not in customer_threads:
        customer_threads[customer_id] = f"thread-{uuid4()}"
    return customer_threads[customer_id]

async def generate_response(user_message: str, customer_telephone:str=None) -> str:
    thread_id = get_or_create_thread_id(customer_telephone)

    # Load-balanced LLM instance
    llm = get_llm()  

    config = {
        "configurable": {
            "thread_id": thread_id,
            "llm": llm,
            "retriever": get_qdrant_retriever()
        }
    }

    input_state = SESSION_STATE.get(thread_id, {
        'messages': [],
        'customer_telephone': customer_telephone,
        'customer_name': None,
        'customer_profession': None,
        'customer_email': None,
        'form_submitted': False
    })

    input_state['messages'].append(HumanMessage(user_message))

    start = perf_counter()
    llm_response = await graph.ainvoke(input_state, config=config)
    end = perf_counter()
    SESSION_STATE[thread_id] = llm_response
    
    llm_response["duration"] = end - start


    logger.info(f"State for {customer_telephone}: {llm_response}")

    if "messages" in llm_response:
        return llm_response["messages"][-1].content
    else:
        logger.warning(f"No se encontró 'messages' en el estado final: {llm_response.keys()}")
        return "Hubo un error al generar la respuesta."