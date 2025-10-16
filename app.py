# app.py
import streamlit as st
import os
import shutil
import subprocess
from pathlib import Path
import json
import hashlib
import time

# Optional imports (used if available)
try:
    import faiss
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SBER = True
except Exception:
    HAS_SBER = False

import numpy as np

# --------------------- Config ---------------------
WORKSPACE = Path.cwd() / "repo_workspace"
INDEX_DIR = WORKSPACE / "indexes"
REPOS_DIR = WORKSPACE / "repos"
WORKSPACE.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)
REPOS_DIR.mkdir(exist_ok=True)

# --------------------- Helpers ---------------------
def clone_repo(repo_url: str, dest: Path):
    dest_str = str(dest)
    if dest.exists():
        return {"status":"exists", "path": dest_str}
    try:
        subprocess.check_output(["git", "clone", repo_url, dest_str], stderr=subprocess.STDOUT)
        return {"status":"cloned", "path": dest_str}
    except subprocess.CalledProcessError as e:
        return {"status":"error", "output": e.output.decode("utf-8", errors="ignore")}

def build_file_tree(root: Path, max_items=5000):
    tree = []
    count = 0
    for p in sorted(root.rglob('*')):
        if count > max_items:
            break
        rel = p.relative_to(root)
        tree.append(str(rel))
        count += 1
    return tree

def read_text_file(path: Path, max_chars=200000):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:max_chars]
    except Exception as e:
        return ""

def chunk_text(text: str, chunk_size=1000, overlap=200):
    # naive chunker by characters approximating tokens
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + chunk_size, L)
        chunks.append(text[start:end])
        start = end - overlap if end < L else end
    return chunks

def get_id(s: str):
    return hashlib.sha1(s.encode()).hexdigest()

# Simple in-memory vector index (fallback if FAISS not present)
class SimpleVectorIndex:
    def __init__(self, dim):
        self.dim = dim
        self.vectors = []  # list of numpy arrays
        self.metadatas = []

    def add(self, vecs, metas):
        for v,m in zip(vecs, metas):
            self.vectors.append(np.array(v, dtype=np.float32))
            self.metadatas.append(m)

    def search(self, qvec, k=5):
        if len(self.vectors) == 0:
            return []
        mats = np.stack(self.vectors, axis=0)  # (N,d)
        # cosine similarity
        q = np.array(qvec, dtype=np.float32)
        mats_norm = mats / (np.linalg.norm(mats, axis=1, keepdims=True) + 1e-9)
        q_norm = q / (np.linalg.norm(q) + 1e-9)
        sims = mats_norm.dot(q_norm)
        idx = np.argsort(-sims)[:k]
        return [{"score": float(sims[i]), "meta": self.metadatas[i]} for i in idx]

# Embedding provider wrapper
class EmbeddingProvider:
    def __init__(self):
        self.model = None
        self.dim = None
        if HAS_SBER:
            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self.dim = self.model.get_sentence_embedding_dimension()
            except Exception:
                self.model = None
                self.dim = 384
        else:
            # fallback dimension
            self.dim = 384

    def embed(self, texts):
        if self.model is not None:
            embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return [list(e.astype(np.float32)) for e in embs]
        else:
            # fallback: random vectors (placeholder) — replace with a real embedding service
            embs = []
            for t in texts:
                rng = np.random.RandomState(int(get_id(t)[:8], 16))
                embs.append(rng.rand(self.dim).astype(np.float32))
            return embs

# --------------------- Streamlit UI ---------------------
st.set_page_config(page_title="RepoMind", layout="wide")
st.title("RepoMind — AI-Powered Repository Analyzer (Streamlit Prototype)")
st.markdown("Prototype UI to clone, inspect, index and query GitHub repositories.")

# Sidebar - repo input and actions
st.sidebar.header("Repository")
repo_url = st.sidebar.text_input("GitHub repo URL", value="https://github.com/psf/requests")
repo_name = st.sidebar.text_input("Local name (optional)")

if not repo_name:
    repo_name = repo_url.rstrip("/").split("/")[-1] if repo_url else ""

clone_col1, clone_col2 = st.sidebar.columns(2)
if clone_col1.button("Clone Repo"):
    if not repo_url:
        st.sidebar.error("Provide a repo URL")
    else:
        dest = REPOS_DIR / repo_name
        res = clone_repo(repo_url, dest)
        if res["status"] == "cloned":
            st.sidebar.success(f"Cloned to {res['path']}")
        elif res["status"] == "exists":
            st.sidebar.info("Repo already exists locally.")
        else:
            st.sidebar.error("Error cloning repo: " + res.get("output","unknown error"))

if clone_col2.button("Delete Local Copy"):
    dest = REPOS_DIR / repo_name
    if dest.exists():
        shutil.rmtree(dest)
        st.sidebar.success("Deleted local copy.")
    else:
        st.sidebar.info("No local copy found.")

# Select repo from local list
st.sidebar.header("Local Repos")
local_repos = sorted([p.name for p in REPOS_DIR.iterdir() if p.is_dir()])
selected = st.sidebar.selectbox("Choose repo", [""] + local_repos)

if selected:
    repo_path = REPOS_DIR / selected
    st.sidebar.write(f"Path: {repo_path}")

# Main area - show files / index / query
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Repository Explorer")
    if selected:
        repo_path = REPOS_DIR / selected
        tree = build_file_tree(repo_path)
        # display first N files and a search box
        qfile = st.text_input("Filter files (substring)", value="")
        N = st.slider("Max files to show", 10, 200, 80)
        filtered = [f for f in tree if qfile.lower() in f.lower()][:N]
        for f in filtered:
            st.code(f)
    else:
        st.info("Clone a repo or pick one from the Local Repos list in the sidebar.")

with col2:
    st.subheader("Index / Search")
    st.markdown("Index the selected repository into an embedding index (FAISS if available, otherwise an in-memory index).")
    if selected:
        repo_path = REPOS_DIR / selected
        index_status_path = INDEX_DIR / f"{selected}_index_meta.json"
        if st.button("Build Index (chunk -> embed -> store)"):
            # gather files
            patterns = [".py", ".md", ".txt", ".json", ".js", ".html"]
            docs = []
            metadatas = []
            for p in repo_path.rglob("*"):
                if p.is_file() and any(p.name.endswith(ext) for ext in patterns):
                    txt = read_text_file(p)
                    if not txt.strip():
                        continue
                    chunks = chunk_text(txt, chunk_size=1200, overlap=200)
                    for i,c in enumerate(chunks):
                        meta = {"file": str(p.relative_to(repo_path)), "chunk_index": i, "repo": selected}
                        docs.append(c)
                        metadatas.append(meta)
            st.write(f"Prepared {len(docs)} chunks for embedding.")
            # embed
            with st.spinner("Loading embedding model..."):
                embprov = EmbeddingProvider()
                embs = embprov.embed(docs)
            st.write(f"Generated {len(embs)} embeddings (dim={embprov.dim}).")
            # store in FAISS if available, else in simple index
            if HAS_FAISS:
                try:
                    import faiss
                    dim = embprov.dim
                    index = faiss.IndexHNSWFlat(dim, 32)
                    import numpy as np
                    emba = np.array(embs, dtype=np.float32)
                    index.add(emba)
                    faiss.write_index(index, str(INDEX_DIR / f"{selected}.index"))
                    # save metadata
                    with open(index_status_path, "w", encoding="utf-8") as fh:
                        json.dump({"repo": selected, "chunks": len(embs), "dim": dim}, fh)
                    st.success("FAISS index built and saved.")
                except Exception as e:
                    st.error("FAISS build error: " + str(e))
            else:
                # fallback: save using numpy arrays + metadata
                try:
                    import numpy as np
                    emba = np.array(embs, dtype=np.float32)
                    np.save(str(INDEX_DIR / f"{selected}_embs.npy"), emba)
                    with open(INDEX_DIR / f"{selected}_meta.json", "w", encoding="utf-8") as fh:
                        json.dump(metadatas, fh)
                    with open(index_status_path, "w", encoding="utf-8") as fh:
                        json.dump({"repo": selected, "chunks": len(embs), "dim": embprov.dim}, fh)
                    st.success("Embeddings saved (FAISS not available).")
                except Exception as e:
                    st.error("Saving embeddings error: " + str(e))
        # search interface
        st.markdown("---")
        st.write("Query the index (semantic search).")
        question = st.text_input("Enter a question to ask the repo:")
        top_k = st.slider("Top K", 1, 10, 5)
        if st.button("Search & Answer"):
            if not question.strip():
                st.error("Enter a question.")
            else:
                # embed question
                embprov = EmbeddingProvider()
                qemb = embprov.embed([question])[0]
                results = []
                if HAS_FAISS and (INDEX_DIR / f"{selected}.index").exists():
                    try:
                        import faiss, numpy as np
                        idx = faiss.read_index(str(INDEX_DIR / f"{selected}.index"))
                        qv = np.array(qemb, dtype=np.float32).reshape(1, -1)
                        D, I = idx.search(qv, top_k)
                        D = D[0].tolist(); I = I[0].tolist()
                        # load docs metadata saved earlier? fallback stored in memory in this prototype
                        mm_path = INDEX_DIR / f"{selected}_meta.json"
                        if mm_path.exists():
                            metas = json.loads(mm_path.read_text(encoding="utf-8"))
                            for i,score in zip(I,D):
                                if i < len(metas):
                                    results.append({"score":float(score), "meta":metas[i]})
                                else:
                                    results.append({"score":float(score), "meta":{"file":"unknown"}})
                        else:
                            for i,score in zip(I,D):
                                results.append({"score":float(score), "meta":{"idx":int(i)}})
                    except Exception as e:
                        st.error("FAISS search error: "+str(e))
                else:
                    # fallback brute-force load
                    try:
                        import numpy as np, math
                        embs_path = INDEX_DIR / f"{selected}_embs.npy"
                        meta_path = INDEX_DIR / f"{selected}_meta.json"
                        if embs_path.exists() and meta_path.exists():
                            emba = np.load(str(embs_path))
                            metas = json.loads(meta_path.read_text(encoding="utf-8"))
                            # cosine similarities
                            q = np.array(qemb, dtype=np.float32)
                            mats = emba / (np.linalg.norm(emba, axis=1, keepdims=True)+1e-9)
                            qn = q / (np.linalg.norm(q)+1e-9)
                            sims = mats.dot(qn)
                            idx = np.argsort(-sims)[:top_k]
                            for i in idx:
                                results.append({"score":float(sims[i]), "meta":metas[i]})
                        else:
                            st.warning("No index found. Build the index first.")
                    except Exception as e:
                        st.error("Fallback search error: "+str(e))
                # display results
                st.write("Top results:")
                for r in results:
                    st.write(r)
                # OPTIONAL: send context + question to LLM (not implemented)
                st.info("LLM answering is not configured in this prototype. Integrate OpenAI/HF Inference to get natural language answers.")

    else:
        st.info("Select a repo to index.")

st.markdown("---")
st.caption("RepoMind Streamlit Prototype — meant for local development. See README for full deployment and integration steps.")
