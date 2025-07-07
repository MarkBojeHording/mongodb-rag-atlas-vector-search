from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware for cross-origin requests (Netlify frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def greet_json():
    return {"Hello": "World!"}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_query = data.get("query", "")
    # Replace this with your RAG logic
    return {"answer": f"You said: {user_query}", "sources": []}
