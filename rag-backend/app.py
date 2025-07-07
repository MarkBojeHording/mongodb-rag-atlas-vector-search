from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    # For now, return a simple response
    # You can add your RAG logic here later
    return {
        "answer": f"Received your question: {request.query}",
        "sources": []
    }
