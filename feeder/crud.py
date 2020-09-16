from sqlalchemy.orm import Session
from tempfile import TemporaryFile
from typing import BinaryIO, List
from datetime import datetime

from . import models, schemas

def list_artifacts(db: Session, tags: List[str], limit: int):
    q = db.query(models.Artifact).join(models.Tag)

    for tag in tags:
        q = q.filter(models.Artifact.tags.any(models.Tag.name == tag))

    return q.limit(limit).all()

def create_artifact(db: Session, artifact: schemas.ArtifactCreate):
    db_artifact = models.Artifact(
        id=artifact.id,
        content_type=artifact.content_type,
        original_file_name=artifact.original_file_name,
        file_size=artifact.file_size,
        created_at=artifact.created_at)
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    return db_artifact

def get_artifact_by_id(db: Session, id: str):
    return db.query(models.Artifact).filter(models.Artifact.id == id).first()

def delete_artifact(db: Session, db_artifact: schemas.Artifact):
    for tag in db_artifact.tags:
        db.delete(tag)

    db.delete(db_artifact)
    db.commit()

def update_artifact(db: Session, db_artifact: schemas.Artifact):
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    return db_artifact

def add_artifact_tag(db: Session, db_artifact: schemas.Artifact, tag: str):
    db_tag = models.Tag(artifact_id=db_artifact.id, name=tag)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_artifact_tag(db: Session, db_artifact: schemas.Artifact, tag: str):
    db_tag = models.Tag(artifact_id=db_artifact.id, name=tag)
    db.delete(db_tag)
    db.commit()

def get_unretained_artifacts(db: Session, now: datetime):
    return db.query(models.Artifact).filter(models.Artifact.retained_until < now).all()