from sqlalchemy import Column, Integer, String
from database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    feedback_text = Column(String, nullable=False)  # ✅ this must match everywhere
