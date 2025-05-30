from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models import User, File
from auth import simple_hash, create_token, get_user_id
import os

router = APIRouter()

@router.post("/signup")
def signup(email: str, password: str, db=Depends(get_db)):
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(400, "Email exists")
    user = User(email=email, password=simple_hash(password), role="client")
    db.add(user)
    db.commit()
    return {"message": "Signed up, ask teacher to verify manually"}

@router.post("/verify")
def verify(email: str, db=Depends(get_db)):
    user = db.query(User).filter_by(email=email, role="client").first()
    if not user:
        raise HTTPException(404)
    user.verified = True
    db.commit()
    return {"message": "Verified"}

@router.post("/login")
def login(email: str, password: str, db=Depends(get_db)):
    user = db.query(User).filter_by(email=email, role="client").first()
    if user and user.verified and simple_hash(password) == user.password:
        return {"token": create_token(user.id)}
    raise HTTPException(401)

@router.get("/files")
def list_files(token: str, db=Depends(get_db)):
    user_id = get_user_id(token)
    user = db.query(User).filter_by(id=user_id, role="client").first()
    if not user or not user.verified:
        raise HTTPException(403)
    files = db.query(File).all()
    return [f.filename for f in files]

@router.get("/download-file/{file_id}")
def download_file(file_id: int, token: str, db=Depends(get_db)):
    user_id = get_user_id(token)
    user = db.query(User).filter_by(id=user_id, role="client").first()
    if not user or not user.verified:
        raise HTTPException(403)
    file = db.query(File).filter_by(id=file_id).first()
    if not file:
        raise HTTPException(404, "File not found")
    return {
        "download_link": f"/static/{file.filename}",
        "message": "success"
    }
