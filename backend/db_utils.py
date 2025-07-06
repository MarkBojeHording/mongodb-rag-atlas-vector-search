# RAG WITH ATLAS VECTOR SEARCH/backend/db_utils.py
# FORCE REDEPLOY - URI encoding fix
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, VECTOR_SEARCH_INDEX_NAME, INVESTOR_PDF_URL, CHUNK_SIZE, CHUNK_OVERLAP
from rag_models import get_embedding
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mongo_collection():
    """Establishes MongoDB connection and returns the collection. MONGO_URI is loaded from environment for security."""

    # MONGO_URI is already encoded in config.py, so use it directly
    if not MONGO_URI:
        raise ValueError("MONGO_URI is not set")

    logger.info(f"Using encoded URI from config: {MONGO_URI[:50]}...")

    try:
        # Try with minimal SSL configuration first
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True,
            w='majority'
        )
        client.admin.command('ping')
        collection = client[DB_NAME][COLLECTION_NAME]
        logger.info("Successfully connected to MongoDB Atlas.")
        return collection
    except Exception as e:
        logger.error(f"Error connecting to MongoDB Atlas: {e}")
        # If the first attempt fails, try with explicit SSL configuration
        try:
            logger.info("Retrying with explicit SSL configuration...")
            client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True,
                retryWrites=True,
                w='majority'
            )
            client.admin.command('ping')
            collection = client[DB_NAME][COLLECTION_NAME]
            logger.info("Successfully connected to MongoDB Atlas with relaxed SSL.")
            return collection
        except Exception as e2:
            logger.error(f"Error connecting to MongoDB Atlas with relaxed SSL: {e2}")
            # Try with no SSL configuration as last resort
            try:
                logger.info("Retrying without SSL configuration...")
                # Remove SSL parameters from URI if present
                uri_without_ssl = MONGO_URI.replace("?ssl=true", "").replace("&ssl=true", "")
                client = MongoClient(
                    uri_without_ssl,
                    serverSelectionTimeoutMS=30000,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000,
                    retryWrites=True,
                    w='majority'
                )
                client.admin.command('ping')
                collection = client[DB_NAME][COLLECTION_NAME]
                logger.info("Successfully connected to MongoDB Atlas without SSL.")
                return collection
            except Exception as e3:
                logger.error(f"Error connecting to MongoDB Atlas without SSL: {e3}")
                raise

def create_vector_search_index(collection):
    """Creates the vector search index (from notebook)."""
    index_name = VECTOR_SEARCH_INDEX_NAME
    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": 768,
                    "path": "embedding",
                    "similarity": "cosine"
                }
            ]
        },
        name=index_name,
        type="vectorSearch"
    )

    try:
        collection.create_search_index(model=search_index_model)
        logger.info(f"Created vector search index: {index_name}")

        # Wait for index to be ready
        print("Polling to check if the index is ready. This may take up to a minute.")
        predicate = lambda index: index.get("queryable") is True

        while True:
            indices = list(collection.list_search_indexes(index_name))
            if len(indices) and predicate(indices[0]):
                break
            time.sleep(5)
        print(f"{index_name} is ready for querying.")

    except Exception as e:
        logger.error(f"Error creating vector search index: {e}")
        raise

def ingest_documents_to_mongodb(pdf_url: str = INVESTOR_PDF_URL):
    """
    Loads PDF, chunks it, generates embeddings, and stores in MongoDB Atlas (from notebook).
    """
    collection = get_mongo_collection()

    logger.info(f"Loading PDF from {pdf_url}...")
    try:
        loader = PyPDFLoader(pdf_url)
        data = loader.load()
        logger.info(f"Loaded {len(data)} pages from PDF.")
    except Exception as e:
        logger.error(f"Error loading PDF from {pdf_url}: {e}")
        raise

    # Split the data into chunks (from notebook)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    documents = text_splitter.split_documents(data)
    logger.info(f"Split PDF into {len(documents)} chunks.")

    # Prepare documents for insertion (from notebook)
    for i, doc in enumerate(documents[:5]):
        logger.info(f"[CHUNK METADATA DEBUG] Chunk {i} metadata: {doc.metadata}")
    docs_to_insert = [{
        "text": doc.page_content,
        "embedding": get_embedding(doc.page_content),
        # Use 'page_label' if present, else fallback to 'page', else None
        "page_number": doc.metadata.get("page_label") or doc.metadata.get("page", None)
    } for doc in documents]

    logger.info("Inserting documents into MongoDB...")
    try:
        result = collection.insert_many(docs_to_insert)
        logger.info(f"Inserted {len(result.inserted_ids)} documents successfully.")

        # Create vector search index
        create_vector_search_index(collection)

    except Exception as e:
        logger.error(f"Error during document insertion: {e}")
        raise

def get_query_results(query):
    """Gets results from a vector search query (from notebook)."""
    collection = get_mongo_collection()
    query_embedding = get_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_SEARCH_INDEX_NAME,
                "queryVector": query_embedding,
                "path": "embedding",
                "exact": True,
                "limit": 3
            }
        }, {
            "$project": {
                "_id": 0,
                "text": 1,
                "page_number": 1
            }
        }
    ]

    results = collection.aggregate(pipeline)
    array_of_results = []
    for doc in results:
        array_of_results.append(doc)
    return array_of_results

if __name__ == "__main__":
    logger.info("Starting document ingestion process...")
    try:
        ingest_documents_to_mongodb()
        logger.info("Document ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
