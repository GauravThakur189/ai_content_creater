import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from wordcloud import STOPWORDS
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

# Load your scraped data
df = pd.read_csv("linkedin_posts.csv")

# Drop rows where text is NaN or 'N/A'
df = df[df['text'].notna()]
df = df[df['text'] != 'N/A']

# --- 1. Most Common Words ---
all_text = ' '.join(df['text'].tolist()).lower()
stopwords = set(STOPWORDS)
words = [word for word in all_text.split() if word not in stopwords and len(word) > 2]
common_words = Counter(words).most_common(20)

print("\n🧠 Most Common Words:")
for word, freq in common_words:
    print(f"{word}: {freq} times")

# Wordcloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud of LinkedIn Posts")
plt.show()

# --- 2. Post Timing Analysis ---

if 'datetime' in df.columns:
    
    def parse_relative_date(text):
      text = str(text).lower()
      if "month" in text:
        num = int(text.split("month")[0].strip().split()[-1])
        return datetime.now() - relativedelta(months=num)
      elif "year" in text:
        num = int(text.split("year")[0].strip().split()[-1])
        return datetime.now() - relativedelta(years=num)
      elif "week" in text:
        num = int(text.split("week")[0].strip().split()[-1])
        return datetime.now() - relativedelta(weeks=num)
      elif "day" in text:
        num = int(text.split("day")[0].strip().split()[-1])
        return datetime.now() - relativedelta(days=num)
      else:
        return None

    df['parsed_date'] = df['datetime'].apply(parse_relative_date)
    df['posting_day'] = df['parsed_date'].dt.day_name()

# Now count post days
    day_counts = df['posting_day'].value_counts()
    print("\n📆 Most Common Posting Days:")
    print(day_counts)

# --- 3. Hashtag Analysis ---
print("Hashtag format")


def extract_hashtags_from_text(text):
    if pd.isna(text):
        return []
    return re.findall(r"#\w+", text)

df['extracted_hashtags'] = df['text'].apply(extract_hashtags_from_text)
all_tags = df['extracted_hashtags'].sum()
hashtag_freq = Counter(all_tags)
print("\n📊 Top 10 Hashtags:")
for tag, count in hashtag_freq.most_common(10):
    print(f"{tag}: {count} times")

# --- 4. Post Length vs Engagement ---
df['post_length'] = df['text'].apply(lambda x: len(str(x)))
df['reactions'] = df['reactions'].str.extract(r'(\d+)').fillna(0).astype(int)
df['comments'] = df['comments'].fillna(0).astype(int)
df['engagement'] = df['reactions'] + df['comments']

plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x='post_length', y='engagement')
plt.title("Post Length vs Engagement")
plt.xlabel("Post Length (Characters)")
plt.ylabel("Engagement (Reactions + Comments)")
plt.tight_layout()
plt.show()
# Top 10 Hashtags Plot
top_tags = dict(hashtag_freq.most_common(10))
plt.figure(figsize=(8, 4))
sns.barplot(x=list(top_tags.values()), y=list(top_tags.keys()))
plt.title("Top Hashtags")
plt.xlabel("Frequency")
plt.tight_layout()
plt.show()

