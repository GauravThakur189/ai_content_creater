import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
import random
import re

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

# Initialize LLM
llm = ChatOpenAI(temperature=0.8, model="gpt-4")

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
    # First parse the insight to extract topic, tone, and CTA
    topic, tone, cta = parse_insight(insight)
    
    # If parsing failed (empty fields), provide default values
    
    prompt_template = ChatPromptTemplate.from_template(
        """
        Based on the following insight, generate a LinkedIn post.
        
        1. Topic: {topic}
        2. Tone: {tone}
        3. CTA: {cta}
        
        you can use these common words : {df_common_words} to create the posts which have been filtered from the previous posts.
        
        The post should feel natural, engaging, and authentic. Keep it under 300 words.
        Also write the some hashtags which are related to the topic of the post.
        you can use these hashtags : {df_hashtags} to create the posts which have been filtered from the previous posts.
        
        Generate {n} different versions.
        """
    )
    
    prompt = prompt_template.format_messages(
        topic=topic, tone=tone, cta=cta, n=n_variations, df_common_words=df_common_words,df_hashtags=df_hashtags
    )
    
   
    try:
      response = llm.invoke(prompt)
    except Exception as e:
       print(f"LLM generation failed: {e}")
       return ["Error generating post variations."]
    
    # Split response by double newline or Version markers if present
    if "\n\nVersion" in response.content:
        variations = re.split(r'\n\nVersion \d+:', response.content)
        # Remove empty strings and strip whitespace
        variations = [v.strip() for v in variations if v.strip()]
    else:
        variations = response.content.strip().split("\n\n")
        # Make sure we have the right number of variations
        if len(variations) < n_variations:
            variations = [v for v in response.content.strip().split("\n") if v.strip()]
            # Group every few lines together to form variations
            grouped_variations = []
            i = 0
            while i < len(variations) and len(grouped_variations) < n_variations:
                group_end = min(i + 5, len(variations))
                grouped_variations.append("\n".join(variations[i:group_end]))
                i = group_end
            variations = grouped_variations[:n_variations]
            print("variations",variations)
    
    # Ensure we have exactly n_variations
    while len(variations) < n_variations:
        variations.append("Alternative LinkedIn post: " + topic)
    
    return variations[:n_variations]

if __name__ == "__main__":
    if not df.empty:
        # Pick a random insight row
        row = random.choice(df.to_dict(orient="records"))
        insight = row["insights"]
        
        print("Generating posts for:\n", insight)

        variations = generate_variations(insight, 3)

        print("\nGenerated LinkedIn Post Variations:\n")
        for i, post in enumerate(variations, start=1):
            print(f"--- Variation {i} ---\n{post}\n")
    else:
        print("No data to process.")


