from fastapi import APIRouter, UploadFile, File as Upload, Depends, HTTPException
from database import get_db
from models import User, File
from auth import get_user_id
import os, shutil

router = APIRouter()
ALLOWED = [".docx", ".pptx", ".xlsx"]
UPLOAD_DIR = "uploads"

@router.post("/login")
def login(email: str, password: str, db=Depends(get_db)):
    from auth import simple_check, create_token
    user = db.query(User).filter_by(email=email, role="ops").first()
    if user and simple_check(password, user.password):
        return {"token": create_token(user.id)}
    raise HTTPException(401, "Invalid login")

@router.post("/upload")
def upload_file(token: str, file: UploadFile = Upload(...), db=Depends(get_db)):
    user_id = get_user_id(token)
    user = db.query(User).filter_by(id=user_id, role="ops").first()
    if not user:
        raise HTTPException(403)
    ext = os.path.splitext(file.filename)[1]
    if ext not in ALLOWED:
        raise HTTPException(400, "Invalid file type")
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    db.add(File(filename=file.filename, uploader_id=user.id))
    db.commit()
    return {"message": "Uploaded successfully"}
