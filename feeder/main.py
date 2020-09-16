from typing import List
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import exc
from hashlib import sha512
from datetime import datetime
import parsedatetime

from .config import settings
from .database import SessionLocal, engine
from .storage import storage
from . import crud, models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def download_url(artifact: schemas.Artifact) -> str:
    path = storage.path_for_key(artifact.id)
    return f"{settings.STORAGE_CDN_BASE_URL}/{path}"

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/artifacts/", response_model=List[schemas.Artifact])
def list_artifacts(tags: str = "", limit: int = 10, db: Session = Depends(get_db)):
    tag_list = tags.split(",")
    tag_list = [t for t in tag_list if t != '']

    if len(tag_list) < 1:
        raise HTTPException(status_code=406, detail="At least one tag must be submitted")

    artifacts = crud.list_artifacts(db=db, tags=tag_list, limit=limit)

    for artifact in artifacts:
        artifact.download_url = download_url(artifact)

    return artifacts

@app.post("/artifacts/", response_model=schemas.Artifact)
def create_artifact(db: Session = Depends(get_db), file: UploadFile = File(default="")):
    h = sha512()
    size = 0

    for chunk in iter(lambda: file.file.read(65535), b''):
        h.update(chunk)
        size += len(chunk)

    artifact = schemas.ArtifactCreate
    artifact.id = h.hexdigest()
    artifact.original_file_name = file.filename
    artifact.content_type = file.content_type
    artifact.file_size = size
    artifact.download_url = download_url(artifact)
    artifact.created_at = datetime.now()

    try:
        crud.create_artifact(db=db, artifact=artifact)

    except exc.IntegrityError:
        raise HTTPException(status_code=304, detail="Tag already exists")

    file.file.seek(0)
    storage.upload(file.file, artifact.id, artifact.content_type)

    return artifact

@app.delete("/artifacts/{id}", response_model=schemas.Artifact)
def delete_artifact_by_id(id: str, db: Session = Depends(get_db)):
    db_artifact = crud.get_artifact_by_id(db=db, id=id)
    if db_artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    storage.delete(key=id)
    crud.delete_artifact(db=db, db_artifact=db_artifact)

    return db_artifact

@app.get("/artifacts/{id}", response_model=schemas.Artifact)
def get_artifact_by_id(id: str, db: Session = Depends(get_db)):
    db_artifact = crud.get_artifact_by_id(db=db, id=id)
    if db_artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    db_artifact.download_url = download_url(db_artifact)

    return db_artifact

@app.post("/artifacts/{id}/retain", response_model=schemas.Artifact)
def set_artifact_retain(id: str, retain: str, db: Session = Depends(get_db)):
    db_artifact = crud.get_artifact_by_id(db=db, id=id)
    if db_artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")

    try:
        c = parsedatetime.Calendar()
        time_struct, _ = c.parse(retain)
        db_artifact.retained_until = datetime(*time_struct[:6])
    except:
        raise HTTPException(status_code=422, detail="Illegal date submitted")

    crud.update_artifact(db=db, db_artifact=db_artifact)
    db_artifact.download_url = download_url(db_artifact)

    return db_artifact

@app.post("/artifacts/{id}/tags/{tag}", response_model=schemas.Artifact)
def add_artifact_tag(id: str, tag: str, db: Session = Depends(get_db)):
    artifact = get_artifact_by_id(db=db, id=id)
    try:
        crud.add_artifact_tag(db=db, db_artifact=artifact, tag=tag)
    except exc.IntegrityError:
        raise HTTPException(status_code=304, detail="Tag already exists")

    return artifact

@app.delete("/artifacts/{id}/tags/{tag}", response_model=schemas.Artifact)
def delete_artifact_tag(id: str, tag: str, db: Session = Depends(get_db)):
    artifact = get_artifact_by_id(db=db, id=id)
    try:
        crud.delete_artifact_tag(db=db, db_artifact=artifact, tag=tag)
    except exc.IntegrityError:
        raise HTTPException(status_code=404, detail="Tag not found")

    return artifact

@app.delete("/purge", response_model=List[schemas.Artifact])
def delete_unretained_artifacts(db: Session = Depends(get_db)):
    db_artifacts = crud.get_unretained_artifacts(db=db, now=datetime.now())

    for db_artifact in db_artifacts:
        storage.delete(key=db_artifact.id)
        crud.delete_artifact(db=db, db_artifact=db_artifact)

    return db_artifacts
