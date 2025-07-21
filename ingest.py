import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch

load_dotenv()

loader = TextLoader("Data/policy.txt", encoding="utf-8")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(docs)

embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",  # your embedding-capable model
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # WITHOUT any /deployments/... suffix
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

vectorstore = AzureSearch.from_documents(
    documents=chunks,
    embedding=embeddings,
    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
)

print("✅ Finished ingesting documents.")