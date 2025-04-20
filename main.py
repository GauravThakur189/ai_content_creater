from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schema, database
import pandas as pd
import random
from generator.posts_generator import generate_variations
from scraper.linkedin_scrapper import run_scraper
from database import SessionLocal
from models import Feedback

# ✅ Create tables BEFORE running any DB operations
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
try:
      df = pd.read_csv("data/post_insights.csv")  # Update with your actual data source
      if 'insights' not in df.columns:
        raise ValueError("DataFrame missing 'insights' column")
except Exception as e:
     df = pd.DataFrame()
     print(f"Data loading error: {str(e)}")    

@app.post("/", response_model=schema.FeedbackResponse)
def create_feedback(feedback: schema.FeedbackCreate, db: Session = Depends(get_db)):
    try:
        db_feedback = Feedback(feedback_text=feedback.feedback_text)
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating feedback: {e}")

@app.post('/scrape')
async def scrape_linkedin(request_data: schema.ProfileRequest):
    """POST endpoint to scrape LinkedIn post variations from DataFrame"""
    
    result = run_scraper(request_data.profile_url)
    return result
       

   
@app.get('/generate')
async def analyze_linkedin():
    """POST endpoint to generate LinkedIn post variations from DataFrame"""
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for processing")
    
    # Select random insight from DataFrame
    row = random.choice(df.to_dict(orient="records"))
    insight = row["insights"]
    
    # Generate variations
    variations = generate_variations(insight, 3)
    # variations = "xyz"
    print("the out vars : ",variations)
    return {
        "original_insight": insight,
        "variations": variations
    }    
