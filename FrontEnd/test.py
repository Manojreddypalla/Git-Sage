import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="RepoMind - AI GitHub Analyzer",
    layout="wide",
    page_icon="🧠"
)

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
st.markdown('<p style="text-align: center; color: #5A5A5A;">AI-Powered GitHub Repository Analyzer - UI Prototype</p>', unsafe_allow_html=True)

# --- SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "repo"

# --- SIDEBAR ---
st.sidebar.markdown('<div class="sidebar-section"><span class="sidebar-title">🧭 Navigation</span></div>', unsafe_allow_html=True)
if st.sidebar.button("📁 Repository Explorer", key="nav_repo"):
    st.session_state.page = "repo"
if st.sidebar.button("🔍 AI Q&A", key="nav_qna"):
    st.session_state.page = "qna"
if st.sidebar.button("🧠 Mind Map", key="nav_map"):
    st.session_state.page = "mindmap"

st.sidebar.markdown('<div class="sidebar-section"><span class="sidebar-title">🔗 GitHub Repository</span></div>', unsafe_allow_html=True)
repo_url = st.sidebar.text_input("Repository URL", placeholder="https://github.com/username/repo", key="repo_url")

if st.sidebar.button("🔁 Clone Repository", key="action_clone"):
    st.sidebar.success("Repository cloned (UI only).")
if st.sidebar.button("🧹 Clear Data", key="action_clear"):
    st.sidebar.warning("Cleared repository data (UI only).")
if st.sidebar.button("📜 Clone History", key="action_history"):
    # Mock dropdown for history
    _ = st.sidebar.selectbox("Previously Cloned", ["psf/requests", "streamlit/streamlit", "huggingface/transformers"], key="history_select")

st.sidebar.markdown('<div class="sidebar-section"><span class="sidebar-title">🤖 AI Actions</span></div>', unsafe_allow_html=True)
if st.sidebar.button("💬 Analyze Repo", key="action_analyze"):
    st.sidebar.info("Analyzing repository (placeholder).")
if st.sidebar.button("📈 Generate Summary", key="action_summary"):
    st.sidebar.info("Summary generated (placeholder).")
if st.sidebar.button("🧩 Detect Key Components", key="action_detect"):
    st.sidebar.info("Key components detected (placeholder).")

st.sidebar.markdown('<div class="sidebar-section"><span class="sidebar-title">⚙️ Settings</span></div>', unsafe_allow_html=True)
theme = st.sidebar.selectbox("Theme", ["Light", "Dark", "Auto"], index=0, key="theme_setting")
st.sidebar.markdown("<div style='margin-top: 2rem;'>Made with ❤️ by Team RepoMind</div>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown("---")
if st.session_state.page == "repo":
    st.subheader("📁 Repository Explorer")
    st.info("This section displays repository structure, files and metadata.")
    st.write("🧩 Placeholder: File tree & details will appear here.")
elif st.session_state.page == "qna":
    st.subheader("🔍 AI Q&A")
    st.info("Ask questions about your repository (LLM logic coming soon).")
    question = st.text_input("💬 Ask a question:", placeholder="e.g., What is this repository for?", key="qna_input")
    if st.button("🚀 Generate Answer", key="qna_button"):
        st.success("🤖 Placeholder: AI answer will appear here.")
elif st.session_state.page == "mindmap":
    st.subheader("🧠 Repository Mind Map")
    st.info("Visualize file connections and dependencies.")
    st.write("🕸️ Placeholder: Mind map visualization will appear here.")

st.markdown("---")
st.caption("© 2025 Team RepoMind | Built with Streamlit")
