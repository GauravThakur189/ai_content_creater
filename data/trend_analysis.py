import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from wordcloud import STOPWORDS

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
# Convert datetime if available
if 'datetime' in df.columns:
    print("format of date time ")
    print(df['datetime'].head(10))

    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime'])

    df['day_of_week'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour

    print("\n📆 Most Common Posting Days:")
    print(df['day_of_week'].value_counts())

    # Plot Day of Week
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x='day_of_week', order=[
                  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.title("Posts per Day of the Week")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Plot Hour of Day
    plt.figure(figsize=(8, 4))
    sns.countplot(data=df, x='hour')
    plt.title("Posts per Hour of Day")
    plt.tight_layout()
    plt.show()
else:
    print("\n⚠️ Posting time data not available or unformatted.")

# --- 3. Hashtag Analysis ---
print("-----------")
print(df['hashtags'].dropna().head(10))
print("----------")
hashtags = df['hashtags'].dropna().tolist()
all_hashtags = ' '.join(hashtags).replace(',', ' ').split()
hashtag_freq = Counter(all_hashtags)

print("\n📊 Top 10 Hashtags:")
for tag, freq in hashtag_freq.most_common(10):
    print(f"{tag}: {freq} times")

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
