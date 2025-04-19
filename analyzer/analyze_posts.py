import csv
from collections import Counter

# 1. Load data from CSV file
def load_csv(filepath):
    posts = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['text'] != "N/A" and row['text'].strip():
              posts.append(row)
    return posts

# 2. Top 5 posts by total engagement (reactions + comments)
def top_posts_by_engagement(posts, top_n=5):
    def get_engagement(post):
        try:
            # Example value: "1,504 reactions" or just "328 reactions"
         reactions_str = post['reactions'].split()[0].replace(',', '') if post['reactions'] else '0'
         comments_str = post['comments'].split()[0].replace(',', '') if post['comments'] else '0'
        
         reactions = int(reactions_str)
         comments = int(comments_str)
        
         return reactions + comments
        except Exception as e:
         print(f"⚠️ Error parsing engagement: {e}")
         return 0
    sorted_posts = sorted(posts, key=get_engagement, reverse=True)
    return sorted_posts[:top_n]

# 3. Most used hashtags
def most_used_hashtags(posts):
    hashtag_list = []
    for post in posts:
        if post['hashtags'] and post['hashtags'].strip():
            # Remove '#' if it's included in values already
            hashtags = [tag.strip().replace('#', '') for tag in post['hashtags'].split(',') if tag.strip()]
            hashtag_list.extend(hashtags)
    return Counter(hashtag_list).most_common(10)


# 4. Post length classifier (short if <100 words)
def classify_post_length(posts):
    short = long = 0
    for post in posts:
        word_count = len(post['text'].split())
        if word_count < 100:
            short += 1
        else:
            long += 1
    return {"short_posts": short, "long_posts": long}

# 5. Run full analysis
def run_analysis():
    filepath = "linkedin_posts.csv"
    posts = load_csv(filepath)

    print("📌 Top 5 Posts by Engagement:\n")
    for post in top_posts_by_engagement(posts):
        print(f"🔹 Text (First 100 chars): {post['text'][:100]}...")
        print(f"❤️ Reactions: {post['reactions']} | 💬 Comments: {post['comments']}\n")

    print("🔥 Most Used Hashtags:\n")
    for tag, count in most_used_hashtags(posts):
        print(f"#{tag}: {count} times")

    print("\n📏 Post Length Summary:\n")
    length_summary = classify_post_length(posts)
    for k, v in length_summary.items():
        print(f"{k.replace('_', ' ').title()}: {v} posts")

# Run analysis
if __name__ == "__main__":
    run_analysis()
