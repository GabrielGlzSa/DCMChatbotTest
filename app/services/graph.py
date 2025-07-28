from langgraph.graph import StateGraph, MessagesState, END 
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal, Optional

from app.core.logger import logger
from app.services.nodes.classification_node import classification_node
from app.services.nodes.entity_recognition_node import entity_recognition_node
from app.services.nodes.greetings_node import greetings_node
from app.services.nodes.contact_info_node import contact_info_node
from app.services.nodes.services_node import retrieve_and_respond_node
from app.services.nodes.fallback_node import fallback_node
from app.services.nodes.submit_form_node import submit_contact_node

def build_chatbot_graph():

    # --- Define the State ---
    class AppState(MessagesState):
        msg_type: Literal["services", "contact_info", "generic_greeting", "spam"]
        customer_phone_number: Optional[str] = None
        customer_name: Optional[str] = None
        customer_profession: Optional[Literal["business owner", "contractor", "dentist", "lawyer"]] = None
        customer_email: Optional[str] = None
        form_submitted: bool = False

    # --- Build the LangGraph ---
    graph = StateGraph(AppState)

    graph.add_node("classification_node", classification_node)
    graph.add_node("entity_recognition_node", entity_recognition_node)
    graph.add_node("greetings_node", greetings_node)
    graph.add_node("contact_info_node", contact_info_node)
    graph.add_node("services_node", retrieve_and_respond_node)
    graph.add_node("submit_contact_node", submit_contact_node)


   

    graph.add_node("fallback_node", fallback_node)


    # Set entry point
    graph.set_entry_point("classification_node")

    graph.add_edge("classification_node", "entity_recognition_node")
    graph.add_edge("greetings_node", "submit_contact_node")
    graph.add_edge("services_node", "submit_contact_node")
    graph.add_edge("contact_info_node", "submit_contact_node")
    graph.add_edge("submit_contact_node", END)

    def routing_function(state: AppState) -> str:
        """
        Routes the state to the appropriate node based on the message type.
        """
        logger.debug(f"State before routing: {state}")
        return_flag = None
        if state['msg_type'] == "generic_greeting":
            return_flag = "greetings"
        elif state['msg_type'] == "contact_info":
            return_flag = "contact_info"
        elif state['msg_type'] == "services":
            if state['customer_profession'] is None:
                return_flag = "contact_info"
            else:
                return_flag = "services"
        else:
            return_flag = "spam"
        logger.debug(f"Routing based on msg_type: {state['msg_type']} to {return_flag}")
        return return_flag
    
    
    graph.add_conditional_edges("entity_recognition_node", routing_function, {
        "greetings": "greetings_node",
        "services": "services_node",
        "contact_info": "contact_info_node",
        "spam": "fallback_node"
    })



    # Stored in RAM so it forgets whenever process is stopped.
    memory = MemorySaver()

    # Compile graph
    return graph.compile(checkpointer=memory)