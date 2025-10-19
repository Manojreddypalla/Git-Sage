import os 
import pandas as pd 
import streamlit as st 
import plotly.express as px 

st.title("📂 Folder Analyzer")
st.write("Analyze all folders and visualize file counts and sizes")



root_dir=st.text_input("enter root directory path :" ,".")

if st.button("Scan Folder"):
    data = []

    for foldername, subfolders, filenames in os.walk(root_dir):
        total_size = 0
        for file in filenames:
            try:
                filepath = os.path.join(foldername, file)
                total_size += os.path.getsize(filepath)
            except Exception:
                pass  # skip unreadable files

        data.append({
            "Folder": foldername,
            "Num_Files": len(filenames),
            "Total_Size_MB": round(total_size / (1024 * 1024), 2)
        })

    df = pd.DataFrame(data)
    st.write("### Folder Data")
    st.dataframe(df)

    # --- Bar Chart ---
    st.write("### 📊 Number of Files per Folder")
    fig1 = px.bar(df, x="Folder", y="Num_Files", title="Files in Each Folder")
    st.plotly_chart(fig1, use_container_width=True)

    # --- Pie Chart ---
    st.write("### 🥧 Folder Size Distribution (MB)")
    fig2 = px.pie(df, values="Total_Size_MB", names="Folder", title="Folder Size Distribution")
    st.plotly_chart(fig2, use_container_width=True)
