from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    class Config:
        orm_mode = True

class ArtifactBase(BaseModel):
    id: str
    file_size: int
    content_type: str
    original_file_name: str

class ArtifactCreate(ArtifactBase):
    pass

class Artifact(ArtifactBase):
    download_url: str = None
    tags: List[Tag] = []
    created_at: datetime
    retained_until: datetime = None

    class Config:
        orm_mode = True