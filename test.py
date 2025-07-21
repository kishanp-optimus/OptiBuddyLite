# test.py
import os
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

# Initialize embeddings
embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# Create vectorstore with a callable embedding function
vectorstore = AzureSearch(
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    embedding_function=embeddings.embed_query,
    search_type="similarity",  # optional
)

def query_index(q: str, k: int = 5):
    return vectorstore.similarity_search(q, k=k)

if __name__ == "__main__":
    q = input("Enter search query: ")
    results = query_index(q)
    if not results:
        print("❌ No documents found.")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Doc #{i} ---")
        print(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
        print(f"Metadata: {doc.metadata}")
