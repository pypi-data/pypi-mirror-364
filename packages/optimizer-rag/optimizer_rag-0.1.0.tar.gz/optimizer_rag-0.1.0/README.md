Document Optimizer for LLMs

A lightweight Python library and Streamlit web application to compress large documents into the most relevant chunks for downstream use in LLM-based workflows.

It leverages semantic chunking, scoring, and selection to reduce token count while preserving essential content, making it ideal for Retrieval-Augmented Generation (RAG), summarization, and QA pipelines.

Features

Token-based document chunk compression

Semantic scoring and chunk selection with Maximal Marginal Relevance (MMR) or similar methods

Integration with LangChain and Groq LLMs

Modular Python package (optimizer) with reusable backend logic

Streamlit frontend for easy document upload and summarization

Supports sentence-transformers for embeddings and tiktoken for token counting

Folder Structure

.
├── app.py (Streamlit frontend application)
├── requirements.txt
├── sample_files/
│ └── sample_doc.txt (Sample input document for testing)
└── optimizer/ (Python module)
├── init.py
├── compressor.py (compress_chunk function)
├── retriever_wrapper.py
├── scorer.py
├── selector.py
└── token_utils.py

Getting Started

Clone the Repository

git clone https://github.com/yourname/document-optimizer.git
cd document-optimizer

Install Requirements

pip install -r requirements.txt

Run the Streamlit App

streamlit run app.py

Usage

As a Python Library

Import the main compression function and run on your document text:

from optimizer.compressor import compress_chunks

chunks = compress_chunks(
 doc_text="...your document text...",
 top_k=5,
 chunk_size=300,
 stride=150,
)

Development

Install Your Package Locally (Editable Mode)

From the root directory:

pip install -e .

This allows you to edit the code in optimizer/ and see changes immediately without reinstalling.

Import Shortcut

optimizer/init.py enables importing key functions directly:

from optimizer import compress_chunks

Technology Stack

Python
Streamlit
LangChain
Sentence-Transformers
Scikit-Learn
Tiktoken
Groq LLMs (optional)