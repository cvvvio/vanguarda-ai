import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E API ---
# O Streamlit busca a chave nos Secrets para não expor no GitHub
try:
    CHAVE_API = st.secrets["GEMINI_CHAVE"]
    genai.configure(api_key=CHAVE_API)
except:
    st.error("Erro: Chave API não encontrada nos Secrets do Streamlit.")
    st.stop()

# --- 2. PERSONALIDADE E CHAIN OF THOUGHT ---
INSTRUCAO_SISTEMA = """
Você é o 'Vanguarda', um assistente de investimentos expert e didático.
Sua missão é ajudar o usuário a entender o mercado financeiro com lógica.

DIFERENCIAL OBRIGATÓRIO (Chain of Thought):
Antes de dar qualquer resposta final, você deve:
1. Identificar o perfil de risco (Conservador, Moderado ou Arrojado).
2. Analisar o cenário econômico (Ex: Selic alta favorece Renda Fixa).
3. Explicar o RACIOCÍNIO por trás da sugestão.

REGRAS: Nunca dê ordens de compra diretas. Foque em educação financeira.
"""

# --- 3. INICIALIZAÇÃO DO MODELO ---
# Usamos o 1.5 Flash pela velocidade na demonstração
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=INSTRUCAO_SISTEMA
)

# --- 4. INTERFACE E UX ---
st.set_page_config(page_title="Vanguarda AI", page_icon="📈", layout="centered")
st.title("📈 Vanguarda: Assistente de Investimentos")
st.caption("Estratégia Financeira com Inteligência Artificial e Chain of Thought")

# Inicializa o histórico de mensagens (Gestão de Contexto)
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibe as mensagens do histórico na tela
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. FLUXO DE CONVERSA ---
if prompt := st.chat_input("Ex: Como a Selic alta afeta meus investimentos?"):
    
    # Mostra a mensagem do usuário
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera a resposta da IA
    with st.chat_message("assistant"):
        # Spinner para feedback visual de processamento (UX)
        with st.spinner("Vanguarda está analisando os dados e raciocinando..."):
            try:
                # Prepara o histórico para manter o contexto
                historico_google = []
                for m in st.session_state.mensagens[:-1]:
                    # Converte o padrão do Streamlit para o padrão da API do Google
                    role_google = "user" if m["role"] == "user" else "model"
                    historico_google.append({"role": role_google, "parts": [m["content"]]})
                
                # Inicia o chat com a memória da conversa
                chat = model.start_chat(history=historico_google)
                response = chat.send_message(prompt)
                
                # Exibe o texto final
                st.markdown(response.text)
                
                # Salva a resposta no histórico
                st.session_state.mensagens.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Ocorreu um erro na geração: {e}")
                st.info("Dica: Verifique se sua cota da API não expirou ou se a chave está correta.")
