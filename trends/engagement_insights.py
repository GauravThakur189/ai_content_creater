import csv
import os
from dotenv import load_dotenv
from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Config
CSV_PATH = "data/linkedin_posts.csv"
OUTPUT_PATH = "data/post_insights.csv"
TOP_N = 3
MODEL_NAME = "gpt-3.5-turbo"

# Initialize LLM
llm = ChatOpenAI(model=MODEL_NAME, temperature=0.3, openai_api_key=OPENAI_API_KEY)

# Clean numeric field from '48 reactions' -> 48
def extract_number(value):
    try:
        return int(''.join(filter(str.isdigit, value)))
    except:
        return 0

# Read and clean CSV
posts = []
with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            text = row.get("text", "").strip()
            reactions = extract_number(row.get("reactions", "0"))
            comments = extract_number(row.get("comments", "0"))
            engagement = reactions + comments
            if text:
                posts.append({"text": text, "reactions": reactions, "comments": comments, "engagement": engagement})
        except Exception as e:
            print(f"Skipping row due to error: {e}")

# Sort by engagement
sorted_posts = sorted(posts, key=itemgetter("engagement"), reverse=True)[:TOP_N]

# Prompt template for LLM
prompt_template = ChatPromptTemplate.from_template("""
Analyze the following LinkedIn post:

Post:
{text}

Extract the following:
1. Main topic
2. Tone
3. Call to action (CTA)
""")

# Analyze top posts
results = []
print("\n🔍 Analyzing top posts with LangChain...")
for post in sorted_posts:
    prompt = prompt_template.format_messages(text=post["text"])
    try:
        response = llm.invoke(prompt)
        summary = response.content.strip()
    except Exception as e:
        summary = f"Error analyzing post: {e}"
    results.append({
        "text_snippet": post["text"][:100].replace("\n", " ") + "...",
        "engagement": post["engagement"],
        "insights": summary
    })

# Save to CSV
with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["text_snippet", "engagement", "insights"])
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Saved insights to {OUTPUT_PATH}")
