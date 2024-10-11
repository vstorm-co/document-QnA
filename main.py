import os

import streamlit as st

from config import config
from file_processor import process_file
from qa_chain import create_qa_chain
from vector_store import get_vectorstore


def main():
    st.set_page_config(page_title="Q&A App", layout="wide")

    st.title("Document Q&A Application")

    # Create uploads directory if it doesn't exist
    if not os.path.exists(config.UPLOAD_FOLDER):
        os.makedirs(config.UPLOAD_FOLDER)

    # Sidebar for file upload and additional information
    with st.sidebar:
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

        if uploaded_file:
            # Save the file locally
            save_path = os.path.join(config.UPLOAD_FOLDER, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File saved locally: {save_path}")

            # Process the uploaded file
            with st.spinner("Processing the uploaded file..."):
                if process_file(save_path):
                    st.success("File processed and added to the knowledge base successfully!")
                else:
                    st.error("An error occurred while processing the file. Please try again.")

        st.subheader("Uploaded Files")
        uploaded_files = os.listdir(config.UPLOAD_FOLDER)
        for file in uploaded_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(file)
            with col2:
                if st.button("Delete", key=f"delete_{file}"):
                    delete_file(file)
                    st.rerun()

    # Main area for Q&A
    st.subheader("Ask a question about the documents")
    user_question = st.text_input("Enter your question:")

    if user_question:
        with st.spinner("Searching for an answer..."):
            vector_store = get_vectorstore()
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            qa_chain = create_qa_chain(retriever)
            result = qa_chain.invoke({"input": user_question})

            # Display the answer
            st.subheader("Answer:")
            st.write(result['answer'])

            # Display the source documents
            st.subheader("Source Documents:")
            for doc in result['context']:
                with st.expander(f"Document: {doc.metadata.get('file_path', 'Unknown')}"):
                    st.write(f"Content: {doc.page_content}")
                    st.write(f"Metadata: {doc.metadata}")


def delete_file(file_name):
    file_path = os.path.join(config.UPLOAD_FOLDER, file_name)
    try:
        os.remove(file_path)
        st.success(f"File {file_name} deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting file {file_name}: {e}")


if __name__ == "__main__":
    main()
