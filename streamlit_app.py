import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Replace with your FastAPI base URL if hosted

st.set_page_config(page_title="LinkedIn Content Creator", layout="centered")

st.title("🤖 LinkedIn Content Creator AI")

# Tab-based layout
tabs = st.tabs(["Scrape LinkedIn", "Generate Posts", "Give Feedback"])

# ======================= Scrape LinkedIn =======================
with tabs[0]:
    st.header("🔍 Scrape LinkedIn Profile")

    profile_url = st.text_input("Enter LinkedIn Profile URL:")
    if st.button("Scrape Now"):
        if profile_url:
            with st.spinner("Scraping profile..."):
                res = requests.post(f"{API_URL}/scrape", json={"profile_url": profile_url})
                if res.status_code == 200:
                    st.success("Scraped successfully!")
                    st.json(res.json())
                else:
                    st.error(f"Failed to scrape: {res.text}")
        else:
            st.warning("Please enter a valid URL.")

# # ======================= Generate Posts =======================

with tabs[1]:
    st.header("📝 Generate Post Variations")
    
    if st.button("Generate from Trending Insights"):
        with st.spinner("Generating post ideas..."):
            res = requests.get(f"{API_URL}/generate")
            if res.status_code == 200:
                data = res.json()

                # ---------------- Original Insight ----------------
                st.subheader("📌 Original Insight")
                original = data["original_insight"]
                st.write(original)

                # ---------------- Variations ----------------
                st.subheader("✍️ AI-Generated Variations")

                variations = data["variations"]
                for variation in variations:
                    if variation.strip() == "---":
                        st.markdown("---")
                    elif variation.strip().startswith("###"):
                        st.markdown(f"**{variation.strip()}**")
                    elif variation.strip().startswith("**Timing to Post:**"):
                        st.subheader("⏰ Timing to Post")
                        st.write(variation.replace("**Timing to Post:**", "").strip())
                    else:
                        st.write(variation.strip())

            else:
                st.error("Error generating post variations. Please try again later.")

# ======================= Feedback =======================
with tabs[2]:
    st.header("💬 Provide Feedback")

    feedback_text = st.text_area("What do you think of the generated posts?")
    if st.button("Submit Feedback"):
        if feedback_text:
            res = requests.post(f"{API_URL}/", json={"feedback_text": feedback_text})
            if res.status_code == 200:
                st.success("Thanks for your feedback!")
            else:
                st.error("Failed to submit feedback.")
        else:
            st.warning("Feedback cannot be empty.")
