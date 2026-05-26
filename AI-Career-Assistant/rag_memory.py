import os
import chromadb
from chromadb.utils import embedding_functions


client = chromadb.PersistentClient(
    path="chroma_memory"
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)


def get_user_collection(username):

    safe_username = username.replace(" ", "_").lower()

    return client.get_or_create_collection(
        name=f"user_memory_{safe_username}",
        embedding_function=openai_ef
    )


def save_memory(username, text, metadata=None):

    collection = get_user_collection(username)

    if metadata is None:
        metadata = {}

    doc_id = str(abs(hash(text)))

    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[doc_id]
    )


def search_memory(username, query, n_results=3):

    collection = get_user_collection(username)

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results

def retrieve_memory_context(username, query, n_results=3):

    results = search_memory(
        username,
        query,
        n_results
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        return ""

    context = "\n\n".join(documents)

    return context
