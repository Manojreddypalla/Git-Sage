import streamlit as st
import ollama

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="RepoMind - AI GitHub Analyzer",
    layout="wide",
    page_icon="🧠"
)

# --- HELPER FUNCTION ---
def get_ollama_models():
    """Fetches the list of available models from the Ollama server."""
    try:
        models = ollama.list().get("models", [])
        return [model["name"] for model in models]
    except Exception:
        return []

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Sidebar width & style */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 300px;
    }
    [data-testid="stSidebar"] .css-1d391kg {
        padding: 1rem 1rem 0 1rem;
    }

    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2B547E;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
    }

    .nav-button button {
        width: 100%;
        border-radius: 8px;
        background-color: #2B547E;
        color: white;
        font-weight: 500;
        padding: 0.5rem 0.8rem;
        margin-top: 0.4rem;
    }
    .nav-button button:hover {
        background-color: #4863A0;
        color: white;
    }

    .sidebar-section {
        margin-bottom: 1.6rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 style="text-align: center; color: #2B547E;">🧠 RepoMind</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #5A5A5A;">AI-Powered GitHub Repository Analyzer</p>', unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "repo"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="sidebar-section"><span class="sidebar-title">🧭 Navigation</span></div>', unsafe_allow_html=True)
    if st.button("📁 Repository Explorer", key="nav_repo"):
        st.session_state.page = "repo"
    if st.button("🔍 AI Q&A", key="nav_qna"):
        st.session_state.page = "qna"
    if st.button("🧠 Mind Map", key="nav_map"):
        st.session_state.page = "mindmap"

    st.markdown('<div class="sidebar-section"><span class="sidebar-title">🔗 GitHub Repository</span></div>', unsafe_allow_html=True)
    repo_url = st.text_input("Repository URL", placeholder="https://github.com/username/repo", key="repo_url")

    if st.button("🔁 Clone Repository", key="action_clone"):
        st.success("Repository cloned (UI only).")
    if st.button("🧹 Clear Data", key="action_clear"):
        st.warning("Cleared repository data (UI only).")
        st.session_state.messages = [] # Also clear chat
        st.rerun()
    if st.button("📜 Clone History", key="action_history"):
        _ = st.selectbox("Previously Cloned", ["psf/requests", "streamlit/streamlit", "huggingface/transformers"], key="history_select")

    st.markdown('<div class="sidebar-section"><span class="sidebar-title">🤖 AI Actions</span></div>', unsafe_allow_html=True)
    if st.button("💬 Analyze Repo", key="action_analyze"):
        st.info("Analyzing repository (placeholder).")
    if st.button("📈 Generate Summary", key="action_summary"):
        st.info("Summary generated (placeholder).")
    if st.button("🧩 Detect Key Components", key="action_detect"):
        st.info("Key components detected (placeholder).")

    st.markdown('<div class="sidebar-section"><span class="sidebar-title">⚙️ Settings</span></div>', unsafe_allow_html=True)
    
    available_models = get_ollama_models()
    
    if available_models:
        # If there's a list of models, create a dropdown
        selected_model = st.selectbox(
            "Select AI Model",
            options=available_models,
            index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
            key="model_selector"
        )
        st.session_state.selected_model = selected_model
    else:
        # If no models are found, show a warning.
        st.warning("Ollama server not detected. Please start it with `ollama serve`.")
        st.session_state.selected_model = None
        
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0, key="theme_setting")
    st.markdown("<div style='margin-top: 2rem;'>Made with ❤️ by Team RepoMind</div>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown("---")

# Page: Repository Explorer
if st.session_state.page == "repo":
    st.subheader("📁 Repository Explorer")
    st.info("This section will display the repository's structure, files, and metadata once cloned.")
    st.write("🧩 Placeholder: A file tree and file content viewer will appear here.")
    st.image("https://placehold.co/800x400/F0F2F6/4B5563?text=File+Tree+Visualization", use_column_width=True)

# Page: AI Q&A
elif st.session_state.page == "qna":
    st.subheader("🔍 AI Q&A")
    st.info("Ask questions about your repository. The AI will respond based on its general knowledge for now.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the code..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if st.session_state.selected_model:
                try:
                    with st.spinner("RepoMind is thinking..."):
                        response = ollama.chat(
                            model=st.session_state.selected_model,
                            messages=st.session_state.messages
                        )
                        full_response = response['message']['content']
                        st.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("No AI model is selected. Please choose a model from the sidebar settings.")

# Page: Mind Map
elif st.session_state.page == "mindmap":
    st.subheader("🧠 Repository Mind Map")
    st.info("This section will visualize the file connections, dependencies, and overall architecture of the repository.")
    st.write("🕸️ Placeholder: A mind map or dependency graph visualization will appear here.")
    st.image("https://placehold.co/800x400/F0F2F6/4B5563?text=Codebase+Mind+Map", use_column_width=True)


st.markdown("---")
st.caption("© 2025 Team RepoMind | Built with Streamlit")

