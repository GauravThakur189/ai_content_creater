import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
import random
import re
import sqlite3  # <-- added

load_dotenv()

# Load post insights
try:
    df = pd.read_csv("data/post_insights.csv")
    df_common_words  = pd.read_csv("common_words_analysis.csv")
    df_hashtags = pd.read_csv("hashtags_analysis.csv")
    df_posting_days = pd.read_csv("posting_days_analysis.csv")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame(columns=["text_snippet", "engagement", "insights"])

# Fetch top 3 feedback from feedback.db
def get_top_feedback():
    try:
        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute("SELECT feedback_text FROM feedbacks DESC LIMIT 2;")
        rows = cursor.fetchall()
        conn.close()
        top_feedback = [row[0] for row in rows]
        return "\n".join(f"- {feedback}" for feedback in top_feedback)
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return ""

top_feedback_text = get_top_feedback()

# Initialize LLM
llm = ChatOpenAI(temperature=0.8, model="gpt-4o")

def parse_insight(insight):
    topic, tone, cta = "", "", ""
    lines = insight.strip().split("\n")
    for line in lines:
        if "topic" in line.lower():
            topic = line.split(":", 1)[1].strip() if ":" in line else ""
        elif "tone" in line.lower():
            tone = line.split(":", 1)[1].strip() if ":" in line else ""
        elif "cta" in line.lower():
            cta = line.split(":", 1)[1].strip() if ":" in line else ""
    return topic, tone, cta

# Function to generate post variations
def generate_variations(insight, n_variations=3):
    topic, tone, cta = parse_insight(insight)

    prompt_template = ChatPromptTemplate.from_template(
        """
        Based on the following insight, generate a LinkedIn post.

        1. Topic: {topic}
        2. Tone: {tone}
        3. CTA: {cta}

        You can use these common words: {df_common_words} to create the posts which have been filtered from the previous posts.
        You can use these hashtags: {df_hashtags} to create the posts which have been filtered from the previous posts.
        
        Here is some top feedback from past posts to guide the style and message:
        {top_feedback}

        The post should feel natural, engaging, and authentic. Keep it under 300 words.
        Also write the some hashtags which are related to the topic of the post.

        Generate {n} different variations in this format
        Variation 1: This is variation one.

        Variation 2: This is variation two.

        Varitaion 3: This is variation three.
        
        Timing To Post: use this data suggestion based on count of timing to post {df_posting_days},
        """
    )

    prompt = prompt_template.format_messages(
        topic=topic, tone=tone, cta=cta,
        n=n_variations, df_common_words=df_common_words,
        df_hashtags=df_hashtags, top_feedback=top_feedback_text,
        df_posting_days=df_posting_days
    )

    try:
        response = llm.invoke(prompt)
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return ["Error generating post variations."]

    if "\n\nVersion" in response.content:
        variations = re.split(r'\n\nVersion \d+:', response.content)
        variations = [v.strip() for v in variations if v.strip()]
    else:
        variations = response.content.strip().split("\n\n")
        if len(variations) < n_variations:
            variations = [v for v in response.content.strip().split("\n") if v.strip()]
            grouped_variations = []
            i = 0
            while i < len(variations) and len(grouped_variations) < n_variations:
                group_end = min(i + 5, len(variations))
                grouped_variations.append("\n".join(variations[i:group_end]))
                i = group_end
            variations = grouped_variations[:n_variations]

    while len(variations) < n_variations:
        variations.append("Alternative LinkedIn post: " + topic)

    return variations

if __name__ == "__main__":
    if not df.empty:
        row = random.choice(df.to_dict(orient="records"))
        insight = row["insights"]

        print("Generating posts for:\n", insight)

        variations = generate_variations(insight, 3)

        print("\nGenerated LinkedIn Post Variations:\n")
        for i, post in enumerate(variations, start=1):
            print(f"--- Variation {i} ---\n{post}\n")
    else:
        print("No data to process.")
