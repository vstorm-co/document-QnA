import os

import streamlit as st

from config import config
from database import get_conversations, save_conversation, init_db
from file_processor import process_file
from qa_chain import create_qa_chain
from utils import generate_conversation_id, get_conversation_folder
from vector_store import get_vectorstore


def main():
    st.set_page_config(page_title="Q&A App", layout="wide")
    st.title("Document Q&A Application")

    conn = init_db()

    if not os.path.exists(config.UPLOAD_FOLDER):
        os.makedirs(config.UPLOAD_FOLDER)

    with st.sidebar:
        st.subheader("Conversations")
        if st.button("Create New Conversation"):
            new_conversation_id = generate_conversation_id()
            save_conversation(conn, new_conversation_id)
            st.success(f"Created new conversation: {new_conversation_id}")

        conversations = get_conversations(conn)
        selected_conversation = st.selectbox(
            "Select a conversation",
            options=[conv[1] for conv in conversations],
            format_func=lambda x: x
        )

        if selected_conversation:
            st.subheader("Upload Documents")
            uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

            if uploaded_file:
                conversation_folder = get_conversation_folder(selected_conversation)
                if not os.path.exists(conversation_folder):
                    os.makedirs(conversation_folder)

                save_path = os.path.join(conversation_folder, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"File saved: {save_path}")

                with st.spinner("Processing the uploaded file..."):
                    if process_file(save_path, namespace=selected_conversation):
                        st.success("File processed and added to the knowledge base successfully!")
                    else:
                        st.error("An error occurred while processing the file. Please try again.")

            st.subheader("Uploaded Files")
            conversation_folder = get_conversation_folder(selected_conversation)
            if os.path.exists(conversation_folder):
                uploaded_files = os.listdir(conversation_folder)
                for file in uploaded_files:
                    st.write(file)
            else:
                st.info("No files uploaded for this conversation yet.")

    if selected_conversation:
        user_question = st.text_input("Enter your question:")

        if user_question:
            with st.spinner("Searching for an answer..."):
                vector_store = get_vectorstore(namespace=selected_conversation)
                retriever = vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
                qa_chain = create_qa_chain(retriever)
                result = qa_chain.invoke({"input": user_question})

                st.subheader("Answer:")
                st.write(result['answer'])

                st.subheader("Source Documents:")
                for doc in result['context']:
                    with st.expander(f"Document: {doc.metadata.get('file_path', 'Unknown')}"):
                        st.write(f"Content: {doc.page_content}")
                        st.write(f"Metadata: {doc.metadata}")
    else:
        st.info("Please select or create a conversation to start.")


if __name__ == "__main__":
    main()
