from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# -----------------------------
# Load embeddings
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Load FAISS
# -----------------------------
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# -----------------------------
# Groq LLaMA Instant
# -----------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# -----------------------------
# Prompt
# -----------------------------
prompt = ChatPromptTemplate.from_template(
    """
    You are an assistant answering questions using only the context below.
    If the answer is not in the context, say "Information not available."

    Context:
    {context}

    Question:
    {question}
    """
)

# -----------------------------
# RAG Chain (LCEL)
# -----------------------------
rag_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
)

# -----------------------------
# Interactive Loop
# -----------------------------
while True:
    query = input("\nAsk a question (or type 'exit'): ")

    if query.lower() == "exit":
        print("Exiting...")
        break

    response = rag_chain.invoke(query)
    print("\nAnswer:\n", response.content)
