import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM  # Corrected import for Ollama
from get_embedding_function import get_embedding_function
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are answering a student's question based only on the following official university registration documents:

{context}

If the context does not contain an answer, say "I don't have enough information to answer that."

Do not make up any information.

---

Answer the question: {question}
"""

# Initialize the model once
model = OllamaLLM(model="mistral", device="cpu")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

def query_rag(query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Retrieve documents with scores
    results = db.similarity_search_with_score(query_text, k=5)

    # Set a threshold to filter out low-quality matches
    RELEVANCE_THRESHOLD = 0.3  # Adjust as needed
    filtered_results = [doc for doc, score in results if score >= RELEVANCE_THRESHOLD]

    # If no highly relevant results, return a fallback message
    if not filtered_results:
        print("No highly relevant documents found. Please refine your query.")
        return {"response": "I'm not sure. Can you ask in a different way?", "sources": []}

    # Concatenate only the most relevant documents
    context_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc in filtered_results]
    formatted_response = {
        "response": response_text,
        "sources": sources,
    }
    print(formatted_response)
    return formatted_response

if __name__ == "__main__":
    main()