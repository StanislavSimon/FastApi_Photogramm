from fastapi import FastAPI, Depends, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Base
import os


Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=RedirectResponse)
def read_root():
    return RedirectResponse(url="/register")


@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(username=username)
    new_user.set_password(password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/index", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.verify_password(password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return RedirectResponse(url="/index", status_code=303)


@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return RedirectResponse(url="/index", status_code=303)


@app.get("/index", response_class=HTMLResponse)
def index(request: Request):
    uploaded_files = os.listdir(UPLOAD_FOLDER)
    return templates.TemplateResponse("index.html", {"request": request, "uploaded_files": uploaded_files})


@app.get("/uploads/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")



