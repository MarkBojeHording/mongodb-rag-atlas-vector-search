# RAG WITH ATLAS VECTOR SEARCH/backend/rag_chain.py
from db_utils import get_query_results
from rag_models import get_llm_client
from config import INVESTOR_PDF_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deduplicate_sources(sources, similarity_threshold=0.8):
    """
    Remove duplicate or very similar sources based on text content.
    """
    unique_sources = []
    seen_texts = set()

    for source in sources:
        # Create a normalized version of the text for comparison
        normalized_text = source["text"].lower().strip()[:100]  # First 100 chars

        if normalized_text not in seen_texts:
            seen_texts.add(normalized_text)
            unique_sources.append(source)

    return unique_sources

def answer_question(query: str) -> dict:
    """
    Performs RAG on the given query using the same approach as the notebook.
    Returns the answer and source documents.
    """
    logger.info(f"Processing query: '{query}'")

    try:
        # Get relevant documents using vector search (from notebook)
        context_docs = get_query_results(query)

        # Deduplicate sources to avoid showing similar chunks
        context_docs = deduplicate_sources(context_docs)

        context_string = " ".join([doc["text"] for doc in context_docs])

        # Construct prompt for the LLM using the retrieved documents as context (from notebook)
        prompt = f"""Use the following pieces of context to answer the question at the end.
        {context_string}
        Question: {query}
        """

        # Use Hugging Face InferenceClient (from notebook)
        llm = get_llm_client()
        if not llm:
            logger.error("LLM client not available")
            return {"answer": "LLM not available. Please check backend logs.", "sources": []}

        # Prompt the LLM (from notebook)
        output = llm.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        # Format answer for readability (add newlines after colons if present)
        answer = output.choices[0].message.content
        if answer:
            # Add a newline after each colon+space for better display
            answer = answer.replace(': ', ':\n')

        # Format sources with page number and link
        sources = []
        for doc in context_docs:
            sources.append({
                "page_content": doc["text"],
                "metadata": {
                    "source": "MongoDB Investor Relations PDF",
                    "page_number": doc.get("page_number", None),
                    "url": INVESTOR_PDF_URL
                }
            })

        logger.info(f"Query processed successfully. Found {len(sources)} unique sources.")
        return {"answer": answer, "sources": sources}

    except Exception as e:
        logger.error(f"Error during RAG query: {e}", exc_info=True)
        return {"answer": f"An error occurred: {e}. Please try again.", "sources": []}

if __name__ == "__main__":
    # Test the RAG chain
    logger.info("Testing RAG chain...")
    sample_question = "What are MongoDB's latest AI announcements?"
    response = answer_question(sample_question)
    print("\n--- RAG Response ---")
    print(f"Question: {sample_question}")
    print(f"Answer: {response['answer']}")
    print("Sources:")
    for i, source in enumerate(response['sources']):
        print(f"  Source {i+1}: {source['page_content'][:150]}...")
