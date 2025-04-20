from fastapi import FastAPI, HTTPException, Depends, HTTPException, status
import pandas as pd
import random
from sqlalchemy.orm import Session
from database import get_db,create_tables
from models import Product
from schema import Feedback
from generator.posts_generator import generate_variations


app = FastAPI()

# Load your DataFrame (replace with actual data loading logic)
try:
    df = pd.read_csv("data/post_insights.csv")  # Update with your actual data source
    if 'insights' not in df.columns:
        raise ValueError("DataFrame missing 'insights' column")
except Exception as e:
    df = pd.DataFrame()
    print(f"Data loading error: {str(e)}")

# def generate_variations(insight: str, count: int) -> list:
#     """Generates variations of the given insight"""
#     return [{"content": f"{insight} - Variation {i+1}"} for i in range(count)]

@app.on_event("startup")
def startup_event():
    create_tables()
@app.get('/posts')
async def get_posts():
    """GET endpoint to retrieve static posts"""
    return [{"title": "Post 1"}, {"title": "Post 2"}]

@app.post('/generate')
async def analyze_linkedin():
    """POST endpoint to generate LinkedIn post variations from DataFrame"""
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for processing")
    
    # Select random insight from DataFrame
    row = random.choice(df.to_dict(orient="records"))
    insight = row["insights"]
    
    # Generate variations
    variations = generate_variations(insight, 3)
    
    return {
        "original_insight": insight,
        "variations": variations
    }
    
    
@app.post("/feedback", status_code=status.HTTP_201_CREATED)
def create_feedback(feedback: Feedback, db: Session = Depends(get_db)):
    """
    Create a new feedback entry
    """
    try:
        # Create new feedback instance
        new_feedback = Product(feedback=feedback.feedback)
        
        # Add to database and commit
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        
        # Return created feedback with ID
        return {
            "id": new_feedback.id,
            "feedback": new_feedback.feedback
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feedback: {str(e)}"
        )    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)