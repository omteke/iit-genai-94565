import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import init_embeddings
from langchain_community.vectorstores import Chroma


RESUME_DIR = "resumes"
CHROMA_DIR = "chroma_db"

os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)


embed_model = init_embeddings(
    model="nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embed_model
)


def extract_and_store(pdf_path=None):
    """Load PDFs, chunk, embed, and store in Chroma"""
    if pdf_path:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
    else:
        loader = DirectoryLoader(
            path=RESUME_DIR,
            glob="*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()

    if not documents:
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )

    chunks = []
    metadatas = []
    resume_names = set()

    # Collect resume names
    for doc in documents:
        resume_name = os.path.basename(doc.metadata["source"])
        resume_names.add(resume_name)

    # Delete old embeddings for these resumes
    for resume in resume_names:
        vectorstore._collection.delete(where={"resume": resume})

    # Create chunks + metadata
    for doc in documents:
        resume_name = os.path.basename(doc.metadata["source"])
        split_texts = splitter.split_text(doc.page_content)

        for i, text in enumerate(split_texts):
            chunks.append(text)
            metadatas.append({
                "resume": resume_name,
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page", -1)
            })

    # Store embeddings
    ids = [f"{meta['resume']}_{i}" for i, meta in enumerate(metadatas)]

    vectorstore._collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids,
        embeddings=embed_model.embed_documents(chunks)
    )

    vectorstore.persist()
    return len(chunks)


def delete_resume(resume_name):
    """Delete resume file and its embeddings"""
    pdf_path = os.path.join(RESUME_DIR, resume_name)

    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    vectorstore._collection.delete(where={"resume": resume_name})
    vectorstore.persist()


def list_resumes():
    return os.listdir(RESUME_DIR)



st.title(" AI Resume Shortlisting")

menu = st.sidebar.radio(
    "Select Action",
    [
        "Upload Resume",
        "List Resumes",
        "Delete Resume",
        "Shortlist Resumes"
    ]
)


if menu == "Upload Resume":
    st.header(" Upload Resume (PDF)")

    uploaded_file = st.file_uploader("Upload resume", type=["pdf"])

    if uploaded_file:
        file_path = os.path.join(RESUME_DIR, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        count = extract_and_store(file_path)
        st.success(f"{uploaded_file.name} indexed ({count} chunks)")


# LIST RESUMES

elif menu == "List Resumes":
    st.header(" Stored Resumes")

    resumes = list_resumes()
    if not resumes:
        st.info("No resumes found")
    else:
        for r in resumes:
            st.write(f"• {r}")


# DELETE RESUME

elif menu == "Delete Resume":
    st.header("🗑 Delete Resume")

    resumes = list_resumes()
    if resumes:
        resume_to_delete = st.selectbox("Select Resume", resumes)

        if st.button("Delete"):
            delete_resume(resume_to_delete)
            st.success(f"{resume_to_delete} deleted")
    else:
        st.info("No resumes to delete")


elif menu == "Shortlist Resumes":
    st.header("Shortlist Resumes")

    job_desc = st.text_area("Paste Job Description")
    top_k = st.number_input("Number of resumes", 1, 10, 3)

    if st.button("Shortlist") and job_desc.strip():
        results = vectorstore.similarity_search(job_desc, k=top_k)

        shortlisted = {}
        for doc in results:
            resume = doc.metadata["resume"]
            shortlisted.setdefault(resume, 0)
            shortlisted[resume] += 1

        st.subheader(" Shortlisted Resumes")
        for r, score in shortlisted.items():
            st.write(f"**{r}** → matched chunks: {score}")
