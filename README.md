# 🧠 LLaMA 3 Chatbot with FastAPI, LangGraph, and Qdrant

This project is a chatbot application powered by **LLaMA 3**, built using **FastAPI** and **LangGraph**, and integrated with:

- 🧠 **LLaMA 3** via `vLLM` for natural language understanding
- 🌐 **FastAPI** for exposing webhook routes
- 🔍 **Qdrant** vector database for semantic memory or document retrieval
- 🤖 Integrated with **GoHighLevel (GHL)** and **WhatsApp**

The chatbot gathers user information (name, profession, email), sends it to **GHL** and stores it in a **Google Spreadsheet**.

---

## 🐳 Docker Compose Services

The project uses **Docker Compose** to orchestrate the following services:

- `fastapi`: The main backend app handling webhooks and LangGraph processing.
- `vllm`: Hosts the LLaMA 3 model for fast inference.
- `qdrant`: Used for vector-based retrieval if needed in the chatbot flow.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/llama3-chatbot.git
cd llama3-chatbot
```

### 2. Create an .env file

For security, all API keys are stored in an .env file. You need to fill the following information.

WHATSAPP_TOKEN=Token obtained from [Meta's developer platform](https://developers.facebook.com/apps/)
WHATSAPP_VERIFY_TOKEN=You create this token and place the same value in your [Meta's developer platform](https://developers.facebook.com/apps/)
GHL_API_KEY= Obtained in the settings of your go high level account.
GHL_LOCATION_ID= Same as above.

### 3. Build and start the services
```bash
docker-compose up --build
```
This will start:

vllm serving the LLaMA 3 model

fastapi backend on http://localhost:8000

qdrant accessible on http://localhost:6333

### 4. Additional info
📬 Webhook Endpoints
POST /test_crm → Receives messages from GHL chat widget

POST /whatsapp → Receives WhatsApp messages