import streamlit as st
import google.generativeai as genai

# 1. CONFIGURAÇÃO DE ACESSO
try:
    CHAVE_API = st.secrets["GEMINI_CHAVE"]
    genai.configure(api_key=CHAVE_API)
except Exception:
    st.error("Erro nos Secrets: Verifique se 'GEMINI_CHAVE' está configurado no painel do Streamlit.")
    st.stop()

# 2. SELEÇÃO AUTOMÁTICA DO MODELO (Blindagem contra Erro 404)
@st.cache_resource
def configurar_ia():
    try:
        # Pede ao Google a lista de nomes que funcionam na sua chave agora
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Procura o Gemini 1.5, se não achar, usa o 1.0 ou o primeiro da lista
        escolhido = next((m for m in modelos if "gemini-1.5-flash" in m), None)
        if not escolhido:
            escolhido = next((m for m in modelos if "gemini-1.0-pro" in m), modelos[0])
            
        instrucao = "Você é o Vanguarda, assistente de investimentos. Use Chain of Thought: explique seu raciocínio lógico antes da conclusão."
        
        return genai.GenerativeModel(model_name=escolhido, system_instruction=instrucao)
    except Exception as e:
        st.error(f"Falha ao conectar com o Google: {e}")
        return None

model = configurar_ia()

# 3. INTERFACE
st.set_page_config(page_title="Vanguarda AI", page_icon="📈")
st.title("📈 Vanguarda: Estratégia de Investimentos")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibe histórico
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE CHAT ESTÁVEL
if prompt := st.chat_input("Diga algo..."):
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Raciocinando..."):
            try:
                # Monta o contexto manualmente (mais estável que o método start_chat)
                historico_texto = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.mensagens])
                
                response = model.generate_content(historico_texto)
                
                st.markdown(response.text)
                st.session_state.mensagens.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Erro na IA: {e}")
