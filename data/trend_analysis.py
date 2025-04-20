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

# Save common words to CSV
common_words_df = pd.DataFrame(common_words, columns=['word', 'frequency'])
common_words_df.to_csv('common_words_analysis.csv', index=False)
print("✅ Common words saved to common_words_analysis.csv")

# --- 2. Post Timing Analysis ---
day_counts_df = None

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
    
    # Save day counts to CSV
    day_counts_df = day_counts.reset_index()
    day_counts_df.columns = ['day_of_week', 'count']
    day_counts_df.to_csv('posting_days_analysis.csv', index=False)
    print("✅ Posting days analysis saved to posting_days_analysis.csv")

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

# Save hashtag analysis to CSV
hashtag_df = pd.DataFrame(hashtag_freq.most_common(), columns=['hashtag', 'frequency'])
hashtag_df.to_csv('hashtags_analysis.csv', index=False)
print("✅ Hashtag analysis saved to hashtags_analysis.csv")

# --- 4. Post Length vs Engagement ---
df['post_length'] = df['text'].apply(lambda x: len(str(x)))
if 'reactions' in df.columns:
    df['reactions'] = df['reactions'].str.extract(r'(\d+)').fillna(0).astype(int)
if 'comments' in df.columns:
    df['comments'] = df['comments'].fillna(0).astype(int)
    df['engagement'] = df['reactions'] + df['comments']

    # Save post length vs engagement analysis
    engagement_df = df[['post_length', 'reactions', 'comments', 'engagement']].copy()
    engagement_df.to_csv('engagement_analysis.csv', index=False)
    print("✅ Engagement analysis saved to engagement_analysis.csv")

# --- 5. Combined Trends Analysis for Content Generation ---
# Create a comprehensive trends file that can be used for post generation
trends_data = {
    'top_words': [word for word, _ in common_words[:10]],
    'top_hashtags': [tag for tag, _ in hashtag_freq.most_common(5)],
    'best_posting_day': day_counts.idxmax() if 'datetime' in df.columns else 'Unknown'
}

if 'engagement' in df.columns:
    # Find optimal post length range based on engagement
    df['length_bucket'] = pd.cut(df['post_length'], bins=[0, 100, 250, 500, 1000, float('inf')], 
                                labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long'])
    avg_engagement_by_length = df.groupby('length_bucket')['engagement'].mean().reset_index()
    best_length = avg_engagement_by_length.loc[avg_engagement_by_length['engagement'].idxmax(), 'length_bucket']
    trends_data['optimal_post_length'] = best_length

# Create DataFrame and save
trends_df = pd.DataFrame([trends_data])
trends_df.to_csv('content_generation_trends.csv', index=False)
print("✅ Combined trends saved to content_generation_trends.csv")

# Print summary of findings for content generation
print("\n🚀 CONTENT GENERATION RECOMMENDATIONS:")
print(f"- Use these popular words: {', '.join(trends_data['top_words'][:5])}")
print(f"- Consider these hashtags: {', '.join(trends_data['top_hashtags'])}")
if 'datetime' in df.columns:
    print(f"- Best day to post: {trends_data['best_posting_day']}")
if 'engagement' in df.columns:
    print(f"- Optimal post length: {trends_data['optimal_post_length']}")