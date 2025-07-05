# RAG WITH ATLAS VECTOR SEARCH/backend/rag_models.py
import os
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient
from config import HF_MODEL_NAME
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_embedding_model = None
_llm_client = None

def get_embedding_model():
    """Initializes and returns the nomic-ai/nomic-embed-text-v1 embedding model (from notebook)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading nomic-ai/nomic-embed-text-v1 embedding model...")
        try:
            # Load the embedding model exactly as in your notebook
            model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

            # Create a wrapper class to make it compatible with LangChain
            class NomicEmbeddings:
                def __init__(self, model):
                    self.model = model

                def embed_documents(self, texts):
                    """Generate embeddings for documents."""
                    embeddings = self.model.encode(texts)
                    return embeddings.tolist()

                def embed_query(self, text):
                    """Generate embedding for a single query."""
                    embedding = self.model.encode([text])
                    return embedding[0].tolist()

            _embedding_model = NomicEmbeddings(model)
            logger.info("Nomic embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Nomic embedding model: {e}")
            _embedding_model = None
    return _embedding_model

def get_llm_client():
    """Initializes and returns the Hugging Face InferenceClient (from notebook)."""
    global _llm_client
    if _llm_client is None:
        logger.info(f"Loading Hugging Face LLM: {HF_MODEL_NAME}")
        try:
            _llm_client = InferenceClient(
                HF_MODEL_NAME,
                token=os.getenv("HUGGINGFACE_TOKEN")
            )
            logger.info(f"Hugging Face LLM '{HF_MODEL_NAME}' loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Hugging Face LLM '{HF_MODEL_NAME}': {e}")
            _llm_client = None
    return _llm_client

def get_embedding(data):
    """Generates vector embeddings for the given data (from notebook)."""
    model = get_embedding_model()
    if model:
        embedding = model.model.encode(data)
        return embedding.tolist()
    else:
        raise ValueError("Embedding model not available")

if __name__ == "__main__":
    # Test model loading
    logger.info("Testing model loading...")
    embed_model = get_embedding_model()
    if embed_model:
        logger.info("Embedding model test: OK")
    else:
        logger.error("Embedding model test: FAILED")

    llm = get_llm_client()
    if llm:
        logger.info("LLM test: OK")
    else:
        logger.error("LLM test: FAILED")
