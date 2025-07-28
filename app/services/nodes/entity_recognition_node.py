
import json
from typing import Dict, Any
import re
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

from app.core.logger import logger
from app.core.embeddings import get_embedding_function

def load_few_shot_examples(file_path: str) -> list:
    examples = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            # Escapamos llaves del output para LangChain.format()
            output_str = json.dumps(row["entities"], ensure_ascii=False)
            escaped_output = output_str.replace("{", "{{").replace("}", "}}")
            examples.append({
                "input": row["input"].strip(),
                "entities": escaped_output
            })
        return examples

fs_entity_examples = load_few_shot_examples("./app/data/few_shot_examples/entity_recognition.jsonl")
embedding_function = get_embedding_function()
db_entity = Chroma(collection_name="entity_recognition_examples", embedding_function=embedding_function)
db_entity.add_texts(
    [e["input"] for e in fs_entity_examples],
    metadatas=fs_entity_examples
)

entity_example_selector = SemanticSimilarityExampleSelector(
    vectorstore=db_entity,
    k=5
)
class_prompt = """You are an assistant that extracts entities from user messages related to marketing clients.

Extract the following entities when present:

- name: person’s full name
- profession: must e one of the following options: 'business', 'lawyer', 'dentist' or 'contractor'
- email: email address
- phone: phone number (digits, with or without separators)

Only include a profession if it exactly matches one of the valid options listed above. If the profession does not match, do not include it in the output.

Format your output as a JSON object with keys for found entities.
If an entity is not present in the message, do not include that key in the output.

Examples:

"""

suffix_class = """Extract entities from the following message. Do not include any additional text or explanation.

Message: {input}
Entities:
"""
# Few shot prompt for message classification.
fs_prompt_entities = FewShotPromptTemplate(
    example_selector=entity_example_selector,
    example_prompt=PromptTemplate(
        input_variables=["input", "entities"],
        template="Message: {input}\nEntities: {entities}"
    ),
    prefix=class_prompt,
    suffix=suffix_class,
    input_variables=["input"]
)

replace_none = re.compile(r'(?i)(:\s*")(null|none|unknown)(?="\s*[,}])')
def fix_json_string(s):
    return replace_none.sub(r'\1None', s)

async def entity_recognition_node(state:Dict[str, Any], config)->Dict[str, Any]:
    """
    Extracts entities from the input text.
    """
    logger.debug(f"State before entity recognition: {state}")
    llm = config['configurable']['llm']

    llm_prompt = fs_prompt_entities.format(input=state['messages'][-1].content)
    logger.info(f'LLM prompt:\n{llm_prompt}')
    llm_response = await llm.ainvoke(llm_prompt)
    logger.info(f'Model response:\n{llm_response.content}')
    try:
        response_text = llm_response.content.strip()
        response_text= fix_json_string(response_text)
        logger.debug(f'Parsed response text: {response_text}')
        detected_entities = eval(response_text)
        logger.debug(f'Parsed entities: {detected_entities}')
        entities = {}
        logger.debug(f"Current customer details: {state['customer_name']}, {state['customer_profession']}, {state['customer_email']}")
        if isinstance(detected_entities, dict):
            for key, value in detected_entities.items():
                if value.strip().lower() not in ["", "unknown", "null", "none"]:
                    if state['customer_name'] is None and key == "name":
                            entities['customer_name'] = value.strip()
                    elif state['customer_profession'] is None and key == "profession":
                        if value.strip().lower() not in ["", "unknown", "null", "none"]:
                            entities['customer_profession'] = value.strip()
                        else:
                            entities['customer_profession'] = None
                    elif state['customer_email'] is None and key == "email":
                        entities['customer_email'] = value.strip()
                    elif state['customer_phone_number'] is None and key == "phone":
                        entities['customer_phone_number'] = value.strip()
            return {**entities}
        else:
            logger.error(f'Invalid response format: {llm_response.content}')
            return {}
    except Exception as e:
        logger.exception('Error parsing entities:')
        return {}