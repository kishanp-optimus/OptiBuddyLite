import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.chat_message_histories.cosmos_db import CosmosDBChatMessageHistory
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = FastAPI()

# -- Setup Cosmos DB memory --
cosmos = CosmosDBChatMessageHistory(
    cosmos_endpoint=os.getenv("COSMOS_ENDPOINT"),
    cosmos_database=os.getenv("COSMOS_DATABASE"),
    cosmos_container=os.getenv("COSMOS_CONTAINER"),
    session_id="default_session",
    user_id="user_1",
    credential=os.getenv("COSMOS_KEY"),
)

# -- Azure Chat Completion Model --
llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

@app.on_event("startup")
async def prepare_cosmos():
    cosmos.prepare_cosmos()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    question = data.get("question", "")

    if not question:
        return JSONResponse({"error": "Question is required"}, status_code=400)

    cosmos.add_user_message(question)

    response = await llm.ainvoke(question)
    cosmos.add_ai_message(response.content)

    return {"answer": response.content}

@app.get("/history")
async def get_history():
    messages = cosmos.messages
    return {
        "history": [
            {"type": m.type, "content": m.content}
            for m in messages
        ]
    }

@app.get("/")
def root():
    return {"message": "Send POST /chat with {'question': ...} and GET /history"}
