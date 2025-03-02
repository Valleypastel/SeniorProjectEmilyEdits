import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are answering a student's question based only on the following official university registration documents:

{context}

Always answer in 250 words or less. Be concise and to the point, not including unecessary details or information. 
If the context does not contain an answer, say "I don't have enough information to answer that."

Do not make up any information.

---

Answer the question based on the above context: {question}
"""


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
    results = db.similarity_search_with_score(query_text, k=3)

    # Set a threshold to filter out low-quality matches
    RELEVANCE_THRESHOLD = 0.3  # Adjust as needed
    filtered_results = [doc for doc, score in results if score >= RELEVANCE_THRESHOLD]

    # If no highly relevant results, return a fallback message
    if not filtered_results:
        print("No highly relevant documents found. Please refine your query.")
        return {"response": "I'm not sure. Can you ask in a different way? Also, the database may need to be updated by the admin.", "sources": []}

    # Concatenate only the most relevant documents
    context_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model=Ollama(model="mistral")
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
