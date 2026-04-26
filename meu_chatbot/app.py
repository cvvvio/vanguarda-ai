import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO ---
CHAVE_API = st.secrets["GEMINI_CHAVE"]
genai.configure(api_key=CHAVE_API)

# Função para encontrar o modelo que sua chave permite usar
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Tentamos o flash primeiro, se não, qualquer um da lista
        for m in available_models:
            if 'gemini-1.5-flash' in m: return m
        return available_models[0]
    except Exception as e:
        return "models/gemini-1.5-flash" # Fallback padrão

# Inicializa o modelo detectado
NOME_DO_MODELO = get_working_model()
model = genai.GenerativeModel(NOME_DO_MODELO)

# 2. IA gera a resposta
    with st.chat_message("assistant"):
        # O Spinner cria aquela animação de "carregando"
        with st.spinner("Vanguarda está raciocinando..."):
            try:
                # Prepara o histórico para o Google
                historico_google = []
                for m in st.session_state.mensagens[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    historico_google.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=historico_google)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.mensagens.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Erro: {e}")
