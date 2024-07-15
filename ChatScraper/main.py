import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.chat import ChatPromptTemplate
import streamlit as st
from scraper import get_informations  
from embeddings import read_txt_file,split_text,create_embeddings,search_with_embeddings

load_dotenv()

model = os.getenv("GOOGLE_DEPLOYMENT")

llm = ChatGoogleGenerativeAI(
    temperature=0.6,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model=model,
    max_tokens=100,
)
assistent = "detetive1.png"
@st.cache_data
def chatbot_interaction(question):
    file_path = "site.txt"
    content = read_txt_file(file_path)
    segments = split_text(content, max_length=8000)
    all_text_segments = []
    all_text_segments.extend(segments)

    embeddings = create_embeddings(all_text_segments)

    best_match_index, best_match_segment = search_with_embeddings(question, embeddings, all_text_segments)

    prompt = ChatPromptTemplate.from_messages([
        ("system",f"""Your name is ChatScraper and you speak Portuguese.
         You're an assistant who helps the user get quick answers via a website that he or she informs you about. 
         Always be direct and polite. Always check the answers in the .txt file you have, don't tell the user.
         Don't make up new information, just use the information provided {best_match_segment}""" ),
        ("user", f"{question}\nConteúdo do site:\n{best_match_segment}")
    ])
    
    prompt_text = prompt.format_prompt(question=question)
    response = llm.invoke(prompt_text)
    return response.content
    
st.set_page_config(page_title="ChatScraper", initial_sidebar_state="auto")

st.markdown(
    f"""
    <div style=" display: flex; justify-content: center; align-items: center; margin-top: 20px;">
        <img src="https://imgur.com/LVlp8AY.png" width="240">
        <h1 style="margin-left: 20px; margin-bottom: 10px;"> ChatScraper</h1>
    </div>
    <h5 style="margin-top: 20px; justify-content: center; align-items: center;">Pesquise rápido pelos seus sites ​🖥️🔍​</h5>
   
    """, unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Informe um site:"}]

for message in st.session_state["messages"]:
    st.chat_message(message["role"],avatar= "detetive1.png").write(message["content"])


if prompt := st.chat_input("Digite aqui:",max_chars=200):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user",avatar="🔍").write(prompt)

    if "http" in prompt:
        try:
            with st.spinner("Coletando informações..."):
                get_informations(prompt)
            st.session_state.messages.append({"role": "assistant", "content": "Informações do site foram coletadas."})
            st.spinner("Processando...")
            st.chat_message("assistant",avatar= "detetive1.png").write("Informações do site foram coletadas.")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Erro ao coletar informações do site: {str(e)}")
    else:
        question = prompt.strip().lower()
        response = chatbot_interaction(question)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant",avatar= "detetive1.png").write(response)
