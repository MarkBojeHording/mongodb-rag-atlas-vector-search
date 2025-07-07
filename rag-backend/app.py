from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chain import answer_question
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str  # Changed from 'question' to 'query' to match frontend

@app.get("/")
def greet_json():
    return {"Hello": "World!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received chat request: {request.query}")

    try:
        # Use the real RAG functionality
        result = answer_question(request.query)

        logger.info(f"RAG response generated successfully")
        return result

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return {
            "answer": f"Sorry, I encountered an error while processing your question. Please try again.",
            "sources": []
        }
