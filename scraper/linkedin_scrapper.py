from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import traceback

# === CONFIG ===
LINKEDIN_EMAIL = "rajanthakur1818@gmail.com"
LINKEDIN_PASSWORD = "Gaurav@189"
PROFILE_URL = "https://www.linkedin.com/in/jaspar-carmichael-jack/"  # Replace
USE_HEADLESS = False  # Set to True to run in headless mode

# === Init Browser ===
def init_browser():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        
        # Optional: Headless mode
        if USE_HEADLESS:
            options.add_argument("--headless=new")
        
        # Performance options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Try with a user agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        print("Browser initialized successfully")
        return driver
    except Exception as e:
        print(f"Failed to initialize browser: {e}")
        print(traceback.format_exc())
        raise

# === Log in to LinkedIn ===
def linkedin_login(driver):
    try:
        print("Navigating to login page...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)  # Give it a moment to load
        
        print("Checking for login form...")
        # Check if we're actually on the login page
        if "login" not in driver.current_url.lower():
            print(f"Warning: Unexpected URL after navigation to login page: {driver.current_url}")
        
        # Wait for username field with increased timeout
        print("Waiting for username field...")
        try:
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            print("Username field found")
        except TimeoutException:
            print("Could not find username field. Current page source:")
            print(driver.page_source[:500] + "...")  # Print part of the page source for debugging
            raise
            
        # Enter credentials
        print("Entering email...")
        username_field.send_keys(LINKEDIN_EMAIL)
        
        print("Finding password field...")
        password_field = driver.find_element(By.ID, "password")
        print("Entering password...")
        password_field.send_keys(LINKEDIN_PASSWORD)
        print("Submitting login form...")
        password_field.send_keys(Keys.RETURN)
        
        # Wait for successful login
        print("Waiting for login to complete...")
        try:
            WebDriverWait(driver, 20).until(
                lambda d: "feed" in d.current_url or "checkpoint" in d.current_url or "voyager" in d.current_url
            )
            print(f"Login complete, current URL: {driver.current_url}")
        except TimeoutException:
            print(f"Login might have failed. Current URL: {driver.current_url}")
            # Continue anyway, as we might still be logged in
        
    except Exception as e:
        print(f"Error during login: {e}")
        print(traceback.format_exc())
        raise

# === Scroll to load more posts ===
def scroll_down(driver, scroll_times=5):
    for i in range(scroll_times):
        print(f"Scrolling down ({i+1}/{scroll_times})...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new posts to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class,"occludable-update")]'))
            )
        except:
            print("Timeout waiting for new posts to load, continuing anyway...")
        
        time.sleep(3)

# Helper functions to extract different elements from posts
def extract_post_text(post):
    possible_xpaths = [
        './/div[contains(@class, "update-components-text")]//span',
        './/span[contains(@dir, "ltr")]',
        './/div[contains(@class, "feed-shared-update-v2__description")]',
        './/div[contains(@class, "feed-shared-text")]//span',
        './/div[contains(@class, "update-components-text-view")]//span',
        './/div[contains(@class, "feed-shared-text-view")]'
    ]
    
    for xpath in possible_xpaths:
        try:
            elements = post.find_elements(By.XPATH, xpath)
            if elements:
                text = " ".join([el.text.strip() for el in elements if el.text.strip()])
                if text:
                    return text
        except Exception as e:
            continue
    
    return "N/A"

def extract_datetime(post):
    possible_xpaths = [
        './/span[contains(@class,"visually-hidden") and contains(text(),"ago")]',
        './/span[contains(@class,"feed-shared-actor__sub-description")]',
        './/span[contains(@class,"update-components-actor__sub-description")]',
        './/span[contains(@aria-hidden,"true") and contains(text(),"•")]',
        './/time',
        './/span[contains(@class,"feed-shared-actor__sub-description")]/span',
        './/span[contains(text(),"ago") and not(contains(@class,"comments"))]'
    ]
    
    for xpath in possible_xpaths:
        try:
            elements = post.find_elements(By.XPATH, xpath)
            for element in elements:
                text = element.text.strip()
                if text and ("ago" in text.lower() or "min" in text.lower() or "hour" in text.lower() or "day" in text.lower()):
                    return text
        except:
            continue
    
    return "unknown"

def extract_reactions(post):
    possible_xpaths = [
        './/span[contains(@aria-label," reactions")]',
        './/button[contains(@aria-label,"reactions")]',
        './/li[contains(@class,"social-details-social-counts__reactions")]'
    ]
    
    for xpath in possible_xpaths:
        try:
            element = post.find_element(By.XPATH, xpath)
            if element:
                if element.get_attribute("aria-label"):
                    return element.get_attribute("aria-label")
                else:
                    text = element.text.strip()
                    if text and any(c.isdigit() for c in text):
                        return text
        except:
            continue
    
    return "0"

def extract_comments(post):
    possible_xpaths = [
        './/button[contains(text()," comment")]',
        './/span[contains(text(),"comments")]',
        './/li[contains(@class,"social-details-social-counts__comments")]'
    ]
    
    for xpath in possible_xpaths:
        try:
            element = post.find_element(By.XPATH, xpath)
            if element:
                text = element.text.strip()
                if text:
                    # Extract only digits
                    digits = ''.join([c for c in text if c.isdigit()])
                    if digits:
                        return digits
        except:
            continue
    
    return "0"

# === Extract post data ===
def extract_posts(driver):
    posts_data = []
    
    # Find all post containers
    posts = driver.find_elements(By.XPATH, '//div[contains(@class,"occludable-update")]')
    print(f"Found {len(posts)} posts to process")
    
    for i, post in enumerate(posts):
        try:
            print(f"Processing post {i+1}/{len(posts)}...")
            
            # Get post elements
            post_text = extract_post_text(post)
            post_datetime = extract_datetime(post)
            reactions = extract_reactions(post)
            comments = extract_comments(post)
            
            # Extract hashtags
            hashtags = [word for word in post_text.split() if word.startswith("#")]
            
            post_data = {
                "text": post_text,
                "datetime": post_datetime,
                "hashtags": ", ".join(hashtags),
                "reactions": reactions,
                "comments": comments
            }
            
            # Add a simple data validation check
            if post_text == "N/A" and post_datetime == "unknown" and reactions == "0" and comments == "0":
                print(f"⚠️ Warning: Post {i+1} has no extractable data")
            
            posts_data.append(post_data)
            
            # Print a sample of the data occasionally to verify extraction
            if i % 20 == 0:
                print(f"Sample data from post {i+1}:")
                print(f"  Text snippet: {post_text[:50]}...")
                print(f"  DateTime: {post_datetime}")
                print(f"  Reactions: {reactions}")
                print(f"  Comments: {comments}")
            
            print(f"✓ Successfully processed post {i+1}")
            
        except Exception as e:
            print(f"✗ Error processing post {i+1}: {e}")
            # Save problematic post HTML for debugging
            try:
                with open(f"debug_post_{i}.html", "w", encoding="utf-8") as f:
                    f.write(post.get_attribute("outerHTML"))
                print(f"  Debug HTML saved to debug_post_{i}.html")
            except Exception as debug_err:
                print(f"  Could not save debug HTML: {debug_err}")

    print(f"Total posts processed: {len(posts_data)}")
    # return posts_data
    posts_data = []
    
    # Find all post containers
    posts = driver.find_elements(By.XPATH, '//div[contains(@class,"occludable-update")]')
    print(f"Found {len(posts)} posts to process")
    
    for i, post in enumerate(posts):
        try:
            print(f"Processing post {i+1}/{len(posts)}...")
            
            # Get post elements
            post_text = extract_post_text(post)
            post_datetime = extract_datetime(post)
            reactions = extract_reactions(post)
            comments = extract_comments(post)
            
            # Extract hashtags
            hashtags = [word for word in post_text.split() if word.startswith("#")]
            
            post_data = {
                "text": post_text,
                "datetime": post_datetime,
                "hashtags": ", ".join(hashtags),
                "reactions": reactions,
                "comments": comments
            }
            
            posts_data.append(post_data)
            print(f"✓ Successfully processed post {i+1}")
            
        except Exception as e:
            print(f"✗ Error processing post {i+1}: {e}")
            # Save problematic post HTML for debugging
            try:
                with open(f"debug_post_{i}.html", "w", encoding="utf-8") as f:
                    f.write(post.get_attribute("outerHTML"))
                print(f"  Debug HTML saved to debug_post_{i}.html")
            except Exception as debug_err:
                print(f"  Could not save debug HTML: {debug_err}")

    return posts_data

# === Save to CSV ===
def save_to_csv(posts, filename=r"C:\Users\GAURAV\OneDrive\Desktop\ai_content_creater\data\linkedin_posts.csv"):
    if not posts:
        print("No posts to save to CSV")
        return
    
    try:
        # Print the current working directory to see where the file will be saved
        import os
        print(f"Saving CSV file to: {os.path.abspath(filename)}")
        
        # Let's check if the file already exists
        if os.path.exists(filename):
            print(f"Warning: File {filename} already exists and will be overwritten")
        
        keys = posts[0].keys()
        with open(filename, "w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(posts)
        
        # Verify the file was actually created
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ {len(posts)} posts saved to CSV: {filename} (Size: {file_size} bytes)")
        else:
            print(f"❌ Error: The file {filename} was not created!")
            
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        import traceback
        traceback.print_exc()

# === Main Run ===
def run_scraper(PROFILE_URL):
    try:
        driver = init_browser()
        print("Browser initialized")
        
        linkedin_login(driver)
        print("Logged in to LinkedIn")
        
        # Navigate to the profile's activity page
        driver.get(PROFILE_URL + "recent-activity/shares/")
        print(f"Navigated to {PROFILE_URL}recent-activity/shares/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"occludable-update")]'))
        )
        print("Activity page loaded")
        
        # Scroll to load more posts
        scroll_down(driver, scroll_times=5)
        
        # Extract posts data
        posts = extract_posts(driver)
        
        # Save to CSV
        if posts:
            save_to_csv(posts)
        else:
            print("⚠️ No posts found to save.")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
    finally:
        print("Closing browser")
        driver.quit()

# === Run it ===
if __name__ == "__main__":
    run_scraper()