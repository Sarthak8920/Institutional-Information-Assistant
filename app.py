import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="CampusConnect_AI of GL Bajaj",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 CampusConnect_AI")
st.caption("Groq LLaMA-3.1 + FAISS + RAG")

# -----------------------------
# Load RAG Chain (cached)
# -----------------------------
@st.cache_resource
def load_rag_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant answering questions using ONLY the context below.
        If the answer is not present, say:
        "Information not available on the website."

        Context:
        {context}

        Question:
        {question}
        """
    )

    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )

    return rag_chain

rag_chain = load_rag_chain()

# -----------------------------
# Session state for chat
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input("Ask about placements, director, packages...")

if user_input:
    # User message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = rag_chain.invoke(user_input)
            answer = response.content
            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
