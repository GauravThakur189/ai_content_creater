# 🚀 LinkedIn Content Creator AI Agent

This project automates and optimizes LinkedIn content creation by analyzing top-performing posts, extracting key trends, and generating personalized content using AI. It also collects user feedback to continuously refine post quality.

---

## 🧠 Project Objective

**Build an AI-powered LinkedIn content assistant** that helps users:
- Understand what content works on LinkedIn
- Scrape insights from thought leaders
- Generate engaging posts using AI
- Improve based on user feedback
- Schedule posts at optimal times (bonus)

---

## 🔧 Tech Stack

- **Backend**: FastAPI  
- **Frontend**: Streamlit  
- **LLM**: OpenAI (via LangChain)  
- **Data Storage**: CSV + SQLite  
- **Scraping**: Custom LinkedIn post parser  
- **Others**: pandas, requests, SQLAlchemy

---

## 🛠 Features

### 📊 1. Track & Analyze LinkedIn Posts
- Scrapes post data from selected profiles
- Stores post content and engagement metrics
- Identifies trends in tone, timing, and calls to action

### 🧠 2. Audience Understanding
- Analyzes scraped content to highlight:
  - Common topics
  - Effective CTAs
  - Ideal tone and timing

### ✍️ 3. AI-Powered Post Generation
- Uses OpenAI (via LangChain) to generate:
  - 2–3 variations of engaging LinkedIn posts
  - Includes hashtags and CTAs
  - Tailored to resemble posts by industry leaders

### 💬 4. User Feedback Loop
- Users can submit feedback
- Helps improve future generations with fine-tuning

### ⏰ 5. Bonus: Post Scheduling (via insights)
- Recommends optimal days/times to post based on analysis

---

## 🖥️ How to Run

```bash
git clone https://github.com/GauravThakur189/ai_content_creater
cd ai_content_creater
pip install -r requirements.txt
uvicorn main:app --reload
streamlit run streamlit_app.py
```
