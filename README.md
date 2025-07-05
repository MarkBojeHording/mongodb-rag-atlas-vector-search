# MongoDB RAG with Atlas Vector Search

A Retrieval Augmented Generation (RAG) application that uses MongoDB Atlas Vector Search to answer questions about MongoDB's investor relations documents.

## Features

- **Vector Search**: Uses MongoDB Atlas Vector Search for semantic document retrieval
- **RAG Pipeline**: Combines document retrieval with Hugging Face's Mistral LLM
- **Modern UI**: React + TypeScript frontend with Tailwind CSS
- **FastAPI Backend**: RESTful API with automatic documentation

## Tech Stack

### Backend
- **FastAPI** - Web framework
- **MongoDB Atlas** - Database with vector search
- **Sentence Transformers** - Embedding model (nomic-ai/nomic-embed-text-v1)
- **Hugging Face** - LLM (Mistral-7B-Instruct-v0.3)
- **LangChain** - Document processing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Setup Instructions

### Prerequisites

1. **Python 3.8+**
2. **Node.js 16+**
3. **MongoDB Atlas Account** with vector search enabled
4. **Hugging Face Account** with access token

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd mongodb-rag-atlas-vector-search
   ```

2. **Create virtual environment**
   ```bash
   python -m venv my_rag_env
   source my_rag_env/bin/activate  # On Windows: my_rag_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Edit `backend/config.py`
   - Replace `YOUR_HUGGING_FACE_TOKEN_HERE` with your HF token
   - Update MongoDB connection string with your cluster details

5. **Start backend server**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

1. **Ingest Documents** (one-time setup)
   - Visit http://localhost:8000/ingest_documents
   - This loads and processes the MongoDB investor PDF

2. **Ask Questions**
   - Use the chat interface to ask questions about MongoDB
   - The system will retrieve relevant documents and generate answers

## API Endpoints

- `GET /` - Health check
- `POST /ask` - Submit a question for RAG processing
- `POST /ingest_documents` - Ingest documents into the vector store

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI server
│   ├── config.py            # Configuration
│   ├── rag_chain.py         # RAG logic
│   ├── rag_models.py        # Models setup
│   ├── db_utils.py          # Database operations
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main component
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Styles
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite config
└── README.md
```

## Configuration

### MongoDB Atlas Setup

1. Create a MongoDB Atlas cluster
2. Enable Atlas Vector Search
3. Create a vector search index:
   ```json
   {
     "fields": [
       {
         "type": "vector",
         "numDimensions": 768,
         "path": "embedding",
         "similarity": "cosine"
       }
     ]
   }
   ```

### Environment Variables

- `HUGGINGFACE_TOKEN` - Hugging Face access token
- `MONGO_URI` - MongoDB Atlas connection string

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
