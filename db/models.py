from sqlalchemy import Column, Integer, VARCHAR, DateTime, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .engine import BaseModel

import enum
from sqlalchemy import Enum as Choice

from typing import List


class Books(BaseModel):

    __tablename__ = "books"

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)

    # Exchange details
    author = Column(VARCHAR(255), unique=False, nullable=False)
    name = Column(VARCHAR(255), unique=False, nullable=False)
    description = Column(VARCHAR(255), unique=False, nullable=True)
    unique_hash = Column(VARCHAR(255), unique=True, nullable=False)
    genre_id = Column(Integer, ForeignKey('genres.id'), nullable=False)
    genre = relationship("Genres", back_populates="books")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return self.name
    

class Genres(BaseModel):

    __tablename__ = "genres"

    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=False, nullable=False)
    books = relationship("Books", back_populates="genre")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return self.name

