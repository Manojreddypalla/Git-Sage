import streamlit as st
import requests
import json

st.title("💬 Ollama Web Interface")
st.write("Talk to your local Ollama model!")

prompt = st.text_area("Enter your prompt:", "Explain quantum computing in simple terms")
model_name = st.text_input("Model name:", "llama3")

if st.button("Run Model"):
    st.write("### Response:")
    with st.spinner("Generating..."):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt},
            stream=True,
        )

        placeholder = st.empty()
        full_reply = ""

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    text = data["response"]
                    # Clean up escaped characters
                    text = text.replace("\\n", "\n").replace("\\t", "    ")
                    full_reply += text
                    placeholder.markdown(full_reply)

        st.success("Done!")
        st.text_area("Full Response:", full_reply, height=200)
