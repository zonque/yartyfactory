from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base

class Tag(Base):
    __tablename__ = "tags"

    name = Column(String, index=True, primary_key=True)
    artifact_id = Column(String, ForeignKey("artifacts.id"), primary_key=True)

    artifact = relationship("Artifact", back_populates="tags")

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, index=True)
    content_type = Column(String)
    file_size = Column(Integer)
    original_file_name = Column(String)
    created_at = Column(DateTime(timezone=True))
    retained_until = Column(DateTime(timezone=True))

    tags = relationship("Tag", back_populates="artifact")