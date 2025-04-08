## Lead_scrapper
A web-scraper that gives you leads, insights and filtered data. 

## Overview

The application performs the following tasks:

- Searches the web based on a user-provided query.
- Extracts company URLs and attempts to pull email contacts from each site.
- Uses a Groq-powered LLM to classify:
  - Whether a company is B2B or B2C.
  - Whether it offers outsourcing services.
  - The industry it belongs to.
- Outputs the results into a structured CSV file.
- Visualizes the data in a clean, interactive dashboard with insights and breakdowns.

## Requirements

- Python 3.8 or above
- A Groq API key (https://console.groq.com/)
- The following Python packages:
  - streamlit
  - requests
  - beautifulsoup4
  - duckduckgo-search
  - python-dotenv
  - pandas
 

## Setup Instructions

- Create your env fiel to store your groq api key
- use the command streamlit run lead_scrapper.py
- put the eda_dashboard.py in a folder called pages so that it can appear on the sidebar
