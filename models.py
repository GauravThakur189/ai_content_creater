from sqlalchemy import Column, Integer, String
from database import Base

class Product(Base):
    __tablename__ = 'feedbacks'  # This is correct based on your error message
    id = Column(Integer, primary_key=True, index=True)
    feedback = Column(String)
    