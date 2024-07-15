import os
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st

@st.cache_data
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content

def split_text(text, max_length=8000):
    words = text.split()
    segments = []
    current_segment = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            segments.append(' '.join(current_segment))
            current_segment = [word]
            current_length = len(word) + 1
        else:
            current_segment.append(word)
            current_length += len(word) + 1

    if current_segment:
        segments.append(' '.join(current_segment))

    return segments

@st.cache_data  
def create_embeddings(all_text_segments):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectors = embeddings_model.embed_documents(all_text_segments)
    return vectors

@st.cache_data
def search_with_embeddings(query, embeddings, all_text_segments):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    query_embedding = embeddings_model.embed_query(query)
   
    scores = [np.dot(query_embedding, emb) for emb in embeddings]

    best_match_index = np.argmax(scores)

    return best_match_index, all_text_segments[best_match_index]