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

# --- 2. INTERFACE ---
st.set_page_config(page_title="Vanguarda AI", page_icon="📈")
st.title("📈 Vanguarda: Assistente de Investimentos")
st.write(f"Conectado via: `{NOME_DO_MODELO}`")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Diga algo..."):
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Forçando o Chain of Thought e Contexto no prompt
            instrucao = "Você é o Vanguarda. Use raciocínio lógico antes de responder."
            contexto = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.mensagens])
            
            response = model.generate_content(f"{instrucao}\n\n{contexto}")
            
            st.markdown(response.text)
            st.session_state.mensagens.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro persistente: {e}")
