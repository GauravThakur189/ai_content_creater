from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    feedback_text: str  # ✅ must match the model's column name

class FeedbackResponse(BaseModel):
    id: int
    feedback_text: str

    class Config:
        orm_mode = True
class ProfileRequest(BaseModel):
    profile_url: str