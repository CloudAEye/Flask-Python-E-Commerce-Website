from flask import Blueprint, request, jsonify
from flask_login import current_user
import chromadb
import openai
import os

rag_bp = Blueprint('rag', __name__)

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("product_knowledge")

openai.api_key = os.environ.get("OPENAI_API_KEY")


def get_embedding(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


@rag_bp.route("/api/ingest", methods=["POST"])
def ingest_document():
    tenant_id = request.json.get("tenant_id")
    document = request.json.get("document")
    doc_id = request.json.get("doc_id")

    embedding = get_embedding(document)

    collection.add(
        documents=[document],
        embeddings=[embedding],
        metadatas=[{"doc_id": doc_id, "type": "product_knowledge"}],
        ids=[doc_id]
    )

    return jsonify({"status": "ingested", "doc_id": doc_id})


@rag_bp.route("/api/search", methods=["POST"])
def search_knowledge():
    query = request.json.get("query")
    tenant_id = request.json.get("tenant_id")
    user_id = request.json.get("user_id")

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    docs = results["documents"][0] if results["documents"] else []
    context = "\n".join(docs)

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Context from knowledge base:\n{context}\n\nCustomer question: {query}"
            }
        ]
    )

    return jsonify({
        "answer": response.choices[0].message.content,
        "sources": docs
    })


@rag_bp.route("/api/ingest/bulk", methods=["POST"])
def bulk_ingest():
    documents = request.json.get("documents", [])
    user_metadata = request.json.get("metadata", {})

    for doc in documents:
        embedding = get_embedding(doc["content"])
        collection.add(
            documents=[doc["content"]],
            embeddings=[embedding],
            metadatas=[user_metadata],
            ids=[doc["id"]]
        )

    return jsonify({"status": "bulk ingested", "count": len(documents)})
