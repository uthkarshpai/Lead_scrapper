import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Lead Scraper EDA", layout="wide")

st.title("📊 Lead Scraper EDA Dashboard")

# File Upload or Select from Directory
uploaded_file = st.file_uploader("Upload a CSV file or select from saved files", type="csv")

# Show files in the local directory that match _leads.csv
default_files = [f for f in os.listdir() if f.endswith("_leads.csv")]

selected_file = None
if not uploaded_file and default_files:
    selected_file = st.selectbox("Or pick from existing files", default_files)

# Load Data
df = None
if uploaded_file:
    df = pd.read_csv(uploaded_file)
elif selected_file:
    df = pd.read_csv(selected_file)
# Clean the B2B/B2C column to extract just "B2B" or "B2C"
df["B2B/B2C"] = df["B2B/B2C"].str.extract(r'\b(B2B|B2C)\b', expand=False)


if df is not None:
    st.success("✅ File loaded successfully!")

    st.subheader("📋 Raw Data Preview")
    st.dataframe(df)

    st.subheader("🔎 Column Summary")
    st.write(df.describe(include='all'))

    # Count of unique values
    st.subheader("📈 Value Counts & Visuals")

    cols_to_analyze = ["B2B/B2C", "Outsourcing?", "Industry"]

    # B2B vs B2C breakdown with filters
if "B2B/B2C" in df.columns:
    st.subheader("🏢 Business Type (B2B/B2C) Breakdown")

    b2_counts = df["B2B/B2C"].value_counts()
    st.write(b2_counts)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total B2B", b2_counts.get("B2B", 0))

    with col2:
        st.metric("Total B2C", b2_counts.get("B2C", 0))

    fig4, ax4 = plt.subplots()
    sns.countplot(x="B2B/B2C", data=df, palette="Set2", order=["B2B", "B2C"])
    ax4.set_ylabel("Count")
    ax4.set_title("Lead Type Distribution")
    st.pyplot(fig4)

    st.markdown("### 🔍 Inspect Leads by Type")
    selected_type = st.radio("Choose type to filter:", ["All", "B2B", "B2C"], horizontal=True)

    if selected_type != "All":
        filtered_df = df[df["B2B/B2C"] == selected_type]
        st.dataframe(filtered_df.reset_index(drop=True))
    else:
        st.dataframe(df.reset_index(drop=True))


    # Email Domains
    st.subheader("📧 Email Domains Breakdown")
    df['Email Domain'] = df['Email'].apply(lambda x: x.split('@')[-1] if pd.notnull(x) else 'unknown')
    domain_counts = df['Email Domain'].value_counts().head(10)

    fig2, ax2 = plt.subplots()
    sns.barplot(x=domain_counts.index, y=domain_counts.values, ax=ax2)
    ax2.set_ylabel("Count")
    ax2.set_title("Top 10 Email Domains")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # Industry vs B2B/B2C breakdown
    if "Industry" in df.columns and "B2B/B2C" in df.columns:
        st.subheader("🏭 Industry vs Business Type")
        cross_tab = pd.crosstab(df["Industry"], df["B2B/B2C"])
        st.dataframe(cross_tab)

        fig3, ax3 = plt.subplots(figsize=(10, 6))
        cross_tab.plot(kind="barh", stacked=True, ax=ax3)
        ax3.set_xlabel("Count")
        ax3.set_title("Industry vs B2B/B2C")
        st.pyplot(fig3)

else:
    st.warning("⚠️ Please upload a file or select one from the list above.")
