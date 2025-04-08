import streamlit as st
import requests
import re
import csv
import os
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Constants
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# Groq LLM Classifier
def ask_groq(text, question):
    prompt = (
        f"You are an intelligent classifier. Based on the following website content, "
        f"please answer the following question briefly.\n\n"
        f"---\nWebsite Content:\n{text[:3000]}\n---\n\nQuestion:\n{question}"
    )

    while True:
        try:
            response = requests.post(GROQ_URL, headers=HEADERS, json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 50
            })

            if response.status_code == 429:
                time.sleep(2)
                continue

            if response.status_code != 200:
                return "Unknown"

            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "Unknown").strip()

        except Exception as e:
            return "Unknown"

# Web scraping helpers
def search_urls(query, pages=3):
    urls = set()
    with DDGS() as ddgs:
        for result in ddgs.text(query, region='in-en', safesearch='Moderate', max_results=pages * 10):
            if "href" in result:
                urls.add(result["href"])
            elif "body" in result and "http" in result["body"]:
                matches = re.findall(r'(https?://[^\s]+)', result["body"])
                urls.update(matches)
    return list(urls)

def extract_emails_from_html(html):
    return list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)))

def scrape_website(url):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            return res.text
    except:
        return ""
    return ""

# Scraper logic
def run_lead_scraper(query, pages):
    urls = search_urls(query, pages)
    results = []

    for url in urls:
        html = scrape_website(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        emails = extract_emails_from_html(html)

        if not emails:
            continue

        email = emails[0]
        b2b = ask_groq(text, "Is this company B2B or B2C?")
        time.sleep(0.5)
        outsource = ask_groq(text, "Does this company offer outsourcing?")
        time.sleep(0.5)
        industry = ask_groq(text, "Which industry does this company belong to?")
        time.sleep(0.5)

        results.append({
            "URL": url,
            "Email": email,
            "B2B/B2C": b2b,
            "Outsourcing?": outsource,
            "Industry": industry
        })

    # Save to CSV
    filename = f"{query.replace(' ', '_')}_leads.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["URL", "Email", "B2B/B2C", "Outsourcing?", "Industry"])
        writer.writeheader()
        writer.writerows(results)

    return results, filename

# ===== Streamlit UI =====
st.set_page_config(page_title="Lead Scraper", layout="wide")
st.title("🔍 Web Lead Scraper using Groq + Streamlit")

query = st.text_input("Enter your search query:")
pages = st.slider("How many result pages to search?", 1, 10, 3)

if st.button("Run Scraper"):
    if not GROQ_API_KEY:
        st.error("❌ GROQ_API_KEY not found. Please set it in your .env file.")
    elif not query.strip():
        st.warning("⚠️ Please enter a query.")
    else:
        with st.spinner("Scraping and analyzing..."):
            results, file = run_lead_scraper(query, pages)
            if results:
                st.success(f"✅ Scraping complete. Saved to {file}")
                st.dataframe(results)
                st.download_button("Download CSV", data=open(file, "rb"), file_name=file, mime="text/csv")
            else:
                st.warning("⚠️ No leads found. Try another query.")

